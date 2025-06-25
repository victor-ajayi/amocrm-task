import asyncio
import logging

import httpx
from asgiref.sync import sync_to_async

from monitor.models import Machine, Metric

logger = logging.getLogger(__name__)


async def fetch_metrics(machine: Machine) -> Metric | None:
    """Fetch metrics from a machine and save them to the database."""
    logger.info(f"Fetching metrics from machine: {machine.name} ({machine.url})")

    try:
        async with httpx.AsyncClient(timeout=5) as client:
            logger.debug(f"Making HTTP request to {machine.url}")

            response = await client.get(machine.url)
            await response.raise_for_status()
            data = await response.json()

            logger.debug(f"Received data from {machine.name}: {data}")

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

            logger.info(
                f"Saved metrics for {machine.name}: CPU={cpu}%, MEM={mem}%, DISK={disk}%, UPTIME={uptime}"
            )

            return metric

    except Exception as e:
        logger.error(f"Failed to fetch metrics from {machine.name}: {e}")


async def poll_machines():
    """Poll all machines for metrics."""
    logger.info("Starting to poll all machines for metrics")

    try:
        machines = await sync_to_async(list)(Machine.objects.all())
        if not machines:
            logger.warning("No machines configured for polling")
            return

        tasks = [fetch_metrics(machine) for machine in machines]
        await asyncio.gather(*tasks)

        logger.info(f"Polled {len(machines)} machines")

    except Exception as e:
        logger.error(f"Error during polling all machines: {e}", exc_info=True)
