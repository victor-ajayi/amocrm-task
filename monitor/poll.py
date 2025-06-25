import asyncio
import logging

import httpx
from asgiref.sync import sync_to_async

from monitor.models import Machine, Metric

logger = logging.getLogger(__name__)


async def fetch_metrics(machine: Machine) -> Metric | None:
    """Fetch metrics from a machine and save them to the database."""

    try:
        async with httpx.AsyncClient(timeout=5) as client:
            logger.debug(f"Making HTTP request to {machine.url}")

            response = await client.get(machine.url)
            await response.raise_for_status()
            data = await response.json()

            cpu = float(data["cpu"])
            mem = float(data["mem"].rstrip("%"))
            disk = float(data["disk"].rstrip("%"))
            uptime = data["uptime"]

            metric = await sync_to_async(Metric.objects.create)(
                machine=machine,
                cpu=cpu,
                mem=mem,
                disk=disk,
                uptime=uptime,
            )

            return metric

    except Exception as e:
        logger.error(f"Failed to fetch metrics from {machine.name}: {e}")


async def poll_machines():
    """Poll all machines for metrics."""
    logger.info("Starting to poll all machines for metrics")

    machines = await sync_to_async(list)(Machine.objects.all())
    if not machines:
        logger.warning("No machines configured for polling")
        return

    tasks = [fetch_metrics(machine) for machine in machines]
    metrics = await asyncio.gather(*tasks)

    from monitor.tasks import run_checks_task

    for metric in metrics:
        if metric:
            run_checks_task.delay(metric.id)

    logger.info(f"Polled {len(machines)} machines")
