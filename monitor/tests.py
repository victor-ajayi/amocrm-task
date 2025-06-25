from unittest.mock import AsyncMock, patch

import pytest
from asgiref.sync import sync_to_async

from monitor.models import Machine, Metric
from monitor.poll import fetch_metrics


@pytest.mark.asyncio
@pytest.mark.django_db
@patch("monitor.poll.httpx.AsyncClient")
async def test_fetch_metrics_success(mock_client):
    machine = await sync_to_async(Machine.objects.create)(
        name="Test Server", url="http://test-server.com/metrics"
    )
    mock_response = AsyncMock()
    mock_response.json = AsyncMock(
        return_value={
            "cpu": "45.2",
            "mem": "67.8%",
            "disk": "23.1%",
            "uptime": "5 days, 3 hours",
        }
    )
    mock_response.raise_for_status = AsyncMock(return_value=None)
    mock_client_instance = AsyncMock()
    mock_client_instance.__aenter__.return_value = mock_client_instance
    mock_client_instance.__aexit__.return_value = None
    mock_client_instance.get.return_value = mock_response
    mock_client.return_value = mock_client_instance

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
@pytest.mark.django_db
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
