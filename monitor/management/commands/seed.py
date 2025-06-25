from django.core.management.base import BaseCommand
from faker import Faker

from monitor.models import Machine


class Command(BaseCommand):
    help = "Seed the Machine model with random data."

    def add_arguments(self, parser):
        parser.add_argument(
            "--number",
            type=int,
            default=30,
            help="Number of machines to create (default: 30)",
        )

    def handle(self, *args, **options):
        number = options["number"]
        fake = Faker()
        created = 0
        for _ in range(number):
            name = fake.hostname()
            url = f"http://{name}/metrics"
            obj, was_created = Machine.objects.get_or_create(name=name, url=url)
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(f"{created} machines created."))
