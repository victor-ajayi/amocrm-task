import logging
from datetime import timedelta

from django.utils import timezone

from monitor.models import THRESHOLDS, Incident, Metric

logger = logging.getLogger(__name__)


def check_cpu(metric: Metric) -> Incident | None:
    """Check CPU threshold for a single metric."""
    if float(metric.cpu) > THRESHOLDS["CPU"]["value"]:
        incident = get_or_create_incident(metric.machine, "CPU", metric.cpu)
        if incident:
            logger.info(
                f"CPU incident triggered for {metric.machine.name} at {metric.cpu}%"
            )
        return incident
    else:
        active_incident = (
            Incident.objects.select_related("machine")
            .filter(machine=metric.machine, type="CPU", end_time__isnull=True)
            .first()
        )
        if active_incident:
            logger.info(f"CPU incident resolved for {metric.machine.name}")
            active_incident.end_time = timezone.now()
            active_incident.save()
    return None


def check_mem(metric: Metric) -> Incident | None:
    """Check memory threshold for a single metric."""
    since = timezone.now() - timedelta(minutes=THRESHOLDS["MEM"]["duration"])

    if float(metric.mem) > THRESHOLDS["MEM"]["value"]:
        recent_incident = (
            Incident.objects.select_related("machine")
            .filter(machine=metric.machine, type="MEM", start_time__gte=since)
            .first()
        )
        if not recent_incident:
            incident = get_or_create_incident(metric.machine, "MEM", metric.mem)
            if incident:
                logger.info(
                    f"MEM incident triggered for {metric.machine.name} at {metric.mem}%"
                )
            return incident
    else:
        active_incident = (
            Incident.objects.select_related("machine")
            .filter(machine=metric.machine, type="MEM", end_time__isnull=True)
            .first()
        )
        if active_incident:
            logger.info(f"MEM incident resolved for {metric.machine.name}")
            active_incident.end_time = timezone.now()
            active_incident.save()
    return None


def check_disk(metric: Metric) -> Incident | None:
    """Check disk threshold for a single metric."""
    since = timezone.now() - timedelta(minutes=THRESHOLDS["DISK"]["duration"])

    if float(metric.disk) > THRESHOLDS["DISK"]["value"]:
        recent_incident = (
            Incident.objects.select_related("machine")
            .filter(machine=metric.machine, type="DISK", start_time__gte=since)
            .first()
        )
        if not recent_incident:
            incident = get_or_create_incident(metric.machine, "DISK", metric.disk)
            if incident:
                logger.info(
                    f"DISK incident triggered for {metric.machine.name} at {metric.disk}%"
                )
            return incident
    else:
        active_incident = (
            Incident.objects.select_related("machine")
            .filter(machine=metric.machine, type="DISK", end_time__isnull=True)
            .first()
        )
        if active_incident:
            logger.info(f"DISK incident resolved for {metric.machine.name}")
            active_incident.end_time = timezone.now()
            active_incident.save()
    return None


def get_or_create_incident(machine, type_, value):
    """Create a new incident if one doesn't already exist."""
    if not Incident.objects.filter(
        machine=machine, type=type_, end_time__isnull=True
    ).exists():
        return Incident.objects.create(
            machine=machine,
            type=type_,
            value=value,
        )
    return None
