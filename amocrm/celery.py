import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "amocrm.settings")

app = Celery("amocrm")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "poll-machines-every-15-minutes": {
        "task": "monitor.tasks.poll_machines_task",
        "schedule": crontab(minute="*/15"),
    },
}
