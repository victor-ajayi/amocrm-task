from django.db import models
from django.utils import timezone

THRESHOLDS = {
    "CPU": {"value": 85, "duration": 0},
    "MEM": {"value": 90, "duration": 30},
    "DISK": {"value": 95, "duration": 120},
}


class Machine(models.Model):
    name = models.CharField(max_length=100)
    url = models.URLField(unique=True)

    def __str__(self):
        return self.name


class Metric(models.Model):
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE)
    cpu = models.FloatField()
    mem = models.FloatField()
    disk = models.FloatField()
    uptime = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.machine.name}: {self.cpu}/{self.mem}%/{self.disk}%"

    def to_dict(self):
        return {
            "cpu": self.cpu,
            "mem": self.mem,
            "disk": self.disk,
            "uptime": self.uptime,
        }


class Incident(models.Model):
    INCIDENT_TYPES = [
        ("CPU", "CPU"),
        ("MEM", "Memory"),
        ("DISK", "Disk"),
    ]

    machine = models.ForeignKey(Machine, on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=INCIDENT_TYPES)
    value = models.FloatField()
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.type} Incident on {self.machine.name}"
