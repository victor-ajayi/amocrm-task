import logging
from datetime import timedelta

from django.utils import timezone

from monitor.models import THRESHOLDS, Incident, Metric

logger = logging.getLogger(__name__)


def check_cpu(metric: Metric) -> Incident | None:
    logger.info(f"Checking CPU for machine {metric.machine.name}: {metric.cpu}%")
    active_incident = Incident.objects.filter(
        machine=metric.machine, type="CPU", end_time__isnull=True
    ).first()

    if float(metric.cpu) > THRESHOLDS["CPU"]["value"]:
        if not active_incident:
            logger.info(
                f"CPU incident triggered for {metric.machine.name} at {metric.cpu}%"
            )
            return create_incident(metric.machine, "CPU", metric.cpu)
    else:
        if active_incident:
            logger.info(f"CPU incident resolved for {metric.machine.name}")
            active_incident.end_time = timezone.now()
            active_incident.save()
        return None


def check_mem(metric: Metric) -> Incident | None:
    logger.info(f"Checking MEM for machine {metric.machine.name}: {metric.mem}%")
    since = timezone.now() - timedelta(minutes=THRESHOLDS["MEM"]["duration"])

    if float(metric.mem) > THRESHOLDS["MEM"]["value"]:
        recent_incident = Incident.objects.filter(
            machine=metric.machine, type="MEM", start_time__gte=since
        ).first()
        if not recent_incident:
            logger.info(
                f"MEM incident triggered for {metric.machine.name} at {metric.mem}%"
            )
            return create_incident(metric.machine, "MEM", metric.mem)
    else:
        active_incident = Incident.objects.filter(
            machine=metric.machine, type="MEM", end_time__isnull=True
        ).first()
        if active_incident:
            logger.info(f"MEM incident resolved for {metric.machine.name}")
            active_incident.end_time = timezone.now()
            active_incident.save()
        return None


def check_disk(metric: Metric) -> Incident | None:
    logger.info(f"Checking DISK for machine {metric.machine.name}: {metric.disk}%")
    since = timezone.now() - timedelta(minutes=THRESHOLDS["DISK"]["duration"])

    if float(metric.disk) > THRESHOLDS["DISK"]["value"]:
        recent_incident = Incident.objects.filter(
            machine=metric.machine, type="DISK", start_time__gte=since
        ).first()
        if not recent_incident:
            logger.info(
                f"DISK incident triggered for {metric.machine.name} at {metric.disk}%"
            )
            return create_incident(metric.machine, "DISK", metric.disk)
    else:
        active_incident = Incident.objects.filter(
            machine=metric.machine, type="DISK", end_time__isnull=True
        ).first()
        if active_incident:
            logger.info(f"DISK incident resolved for {metric.machine.name}")
            active_incident.end_time = timezone.now()
            active_incident.save()
        return None


def create_incident(machine, type_, value):
    logger.info(f"Creating incident: {type_} for {machine.name} at value {value}")
    if not Incident.objects.filter(
        machine=machine, type=type_, end_time__isnull=True
    ).exists():
        Incident.objects.create(
            machine=machine,
            type=type_,
            value=value,
        )
