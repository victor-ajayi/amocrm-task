from django.db import models


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
