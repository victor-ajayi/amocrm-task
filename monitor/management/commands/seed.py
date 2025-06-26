from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker

from monitor.models import Incident, Machine, Metric


class Command(BaseCommand):
    help = "Seed all models with random data."

    def add_arguments(self, parser):
        parser.add_argument(
            "--machines",
            type=int,
            default=5,
            help="Number of machines to create (default: 5)",
        )
        parser.add_argument(
            "--metrics",
            type=int,
            default=20,
            help="Number of metrics to create per machine (default: 20)",
        )
        parser.add_argument(
            "--incidents",
            type=int,
            default=10,
            help="Number of incidents to create (default: 10)",
        )

    def handle(self, *args, **options):
        machines_count = options["machines"]
        metrics_per_machine = options["metrics"]
        incidents_count = options["incidents"]

        fake = Faker()

        # Create machines
        machines = self.create_machines(fake, machines_count)

        # Create metrics for each machine
        metrics = self.create_metrics(fake, machines, metrics_per_machine)

        # Create incidents
        incidents = self.create_incidents(fake, machines, incidents_count)

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully created {len(machines)} machines, "
                f"{len(metrics)} metrics, and {len(incidents)} incidents."
            )
        )

    def create_machines(self, fake, count):
        """Create sample machines."""
        machines = []
        created = 0

        for _ in range(count):
            name = fake.hostname()
            url = f"http://{name}/metrics"
            machine, was_created = Machine.objects.get_or_create(name=name, url=url)
            machines.append(machine)
            if was_created:
                created += 1
                self.stdout.write(f"Created machine: {machine.name}")

        if created > 0:
            self.stdout.write(f"Created {created} new machines")

        return machines

    def create_metrics(self, fake, machines, metrics_per_machine):
        """Create sample metrics for each machine."""
        metrics = []
        current_time = timezone.now()

        for machine in machines:
            for i in range(metrics_per_machine):
                # Generate realistic metric values
                cpu = fake.random_int(min=20, max=100)
                mem = fake.random_int(min=30, max=100)
                disk = fake.random_int(min=40, max=100)
                uptime = f"{fake.random_int(min=1, max=30)}d {fake.random_int(min=0, max=23)}h"

                # Create timestamp (some recent, some older)
                timestamp = current_time - timedelta(
                    hours=fake.random_int(min=0, max=168)  # 0-7 days ago
                )

                metric = Metric.objects.create(
                    machine=machine,
                    cpu=cpu,
                    mem=mem,
                    disk=disk,
                    uptime=uptime,
                    timestamp=timestamp,
                )
                metrics.append(metric)

        self.stdout.write(
            f"Created {len(metrics)} metrics across {len(machines)} machines"
        )
        return metrics

    def create_incidents(self, fake, machines, count):
        """Create sample incidents with realistic data."""
        incident_types = ["CPU", "MEM", "DISK"]
        current_time = timezone.now()
        incidents = []

        for i in range(count):
            # Pick a random machine
            machine = fake.random_element(machines)

            # Pick a random incident type
            incident_type = fake.random_element(incident_types)

            # Generate realistic values based on type
            if incident_type == "CPU":
                value = fake.random_int(min=85, max=99)
            elif incident_type == "MEM":
                value = fake.random_int(min=90, max=99)
            else:  # DISK
                value = fake.random_int(min=95, max=99)

            # Create start time (some recent, some older)
            if i < count // 2:
                # Recent incidents (active) - started within last 24 hours
                start_time = current_time - timedelta(
                    hours=fake.random_int(min=1, max=24)
                )
                end_time = None
            else:
                # Older incidents (resolved) - started 1-7 days ago, ended exactly 1 day after start
                days_ago = fake.random_int(min=1, max=7)
                hours_ago = fake.random_int(min=0, max=23)
                start_time = current_time - timedelta(days=days_ago, hours=hours_ago)

                # End time is exactly 1 day after start time
                end_time = start_time + timedelta(days=1)

            incident = Incident.objects.create(
                machine=machine,
                type=incident_type,
                value=value,
                start_time=start_time,
                end_time=end_time,
            )
            incidents.append(incident)

            status = "Active" if end_time is None else "Resolved"
            self.stdout.write(
                f"Created {incident_type} incident on {machine.name}: {value}% ({status})"
            )

        return incidents
