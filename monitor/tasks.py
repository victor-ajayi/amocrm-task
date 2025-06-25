import asyncio

from celery import shared_task

from monitor.poll import poll_machines


@shared_task
def poll_machines_task():
    asyncio.run(poll_machines())
