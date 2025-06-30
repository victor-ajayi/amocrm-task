from unittest.mock import AsyncMock, Mock, patch

import pytest
from asgiref.sync import sync_to_async

from monitor.models import Incident, Machine, Metric
from monitor.poll import fetch_metrics, poll_machines


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


@pytest.fixture(autouse=True)
def clear_db(db):
    yield
    Machine.objects.all().delete()
    Metric.objects.all().delete()
    Incident.objects.all().delete()


@pytest.mark.asyncio
@patch("monitor.poll.httpx.AsyncClient")
async def test_fetch_metrics_success(mock_client):

    mock_response = AsyncMock()
    mock_response.json = AsyncMock(
        return_value={
            "cpu": "45.2",
            "mem": "67.8%",
            "disk": "23.1%",
            "uptime": "5 days, 3 hours",
        }
    )
    mock_response.raise_for_status = Mock(return_value=None)
    mock_client_instance = AsyncMock()
    mock_client_instance.__aenter__.return_value = mock_client_instance
    mock_client_instance.__aexit__.return_value = None
    mock_client_instance.get.return_value = mock_response
    mock_client.return_value = mock_client_instance

    machine = await sync_to_async(Machine.objects.create)(
        name="Test Server", url="http://test-server.com/metrics"
    )
    result = await fetch_metrics(machine)

    assert result is not None
    assert result.machine == machine
    assert result.cpu == 45.2
    assert result.mem == 67.8
    assert result.disk == 23.1
    assert result.uptime == "5 days, 3 hours"
    saved_metric = await sync_to_async(Metric.objects.get)(machine=machine)
    assert saved_metric.cpu == 45.2
    assert saved_metric.mem == 67.8


@pytest.mark.asyncio
@patch("monitor.poll.httpx.AsyncClient")
async def test_fetch_metrics_failed(mock_client):
    machine = await sync_to_async(Machine.objects.create)(
        name="Test Server 2", url="http://test-server-2.com/metrics"
    )
    mock_client_instance = AsyncMock()
    mock_client_instance.__aenter__.return_value = mock_client_instance
    mock_client_instance.__aexit__.return_value = None
    mock_client_instance.get.side_effect = Exception("Connection failed")
    mock_client.return_value = mock_client_instance

    result = await fetch_metrics(machine)
    assert result is None
    assert not await sync_to_async(Metric.objects.filter(machine=machine).exists)()


@pytest.mark.asyncio
@patch("monitor.poll.httpx.AsyncClient")
@patch("monitor.tasks.run_checks_task")
async def test_incident_created_on_high_cpu(mock_run_checks_task, mock_client):
    machine = await sync_to_async(Machine.objects.create)(
        name="Test Server 3", url="http://test-server-3.com/metrics"
    )
    mock_response = AsyncMock()
    mock_response.json = AsyncMock(
        return_value={
            "cpu": "99.0",
            "mem": "10%",
            "disk": "10%",
            "uptime": "1d",
        }
    )
    mock_response.raise_for_status = Mock(return_value=None)
    mock_client_instance = AsyncMock()
    mock_client_instance.__aenter__.return_value = mock_client_instance
    mock_client_instance.__aexit__.return_value = mock_client_instance
    mock_client_instance.get.return_value = mock_response
    mock_client.return_value = mock_client_instance

    await poll_machines()

    metric = await sync_to_async(Metric.objects.get)(machine=machine)

    from monitor.incident import check_cpu

    await sync_to_async(check_cpu)(metric)

    # Check that an incident was created for high CPU
    incident_exists = await sync_to_async(Incident.objects.filter)(
        machine=machine, type="CPU", end_time__isnull=True
    )
    assert await sync_to_async(incident_exists.exists)()
