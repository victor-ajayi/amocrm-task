import asyncio
import logging

from celery import shared_task

from monitor.incident import check_cpu, check_disk, check_mem
from monitor.models import Metric
from monitor.poll import poll_machines

logger = logging.getLogger(__name__)


@shared_task
def poll_machines_task():
    asyncio.run(poll_machines())

@shared_task
def run_checks_task(metric_id):
    try:
        metric = Metric.objects.get(id=metric_id)

        check_cpu(metric)
        check_mem(metric)
        check_disk(metric)

    except Exception as e:
        logger.error(
            f"Error in run_checks_task for metric_id {metric_id}: {e}", exc_info=True
        )
