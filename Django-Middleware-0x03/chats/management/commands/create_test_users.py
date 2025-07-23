from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from faker import Faker

User = get_user_model()


class Command(BaseCommand):
    help = "Create test users for development with fake data."

    def add_arguments(self, parser):
        parser.add_argument(
            "--count", type=int, default=5, help="Number of users to create"
        )

    @transaction.atomic
    def handle(self, *args, **options):
        count = options["count"]
        fake = Faker()
        created_count = 0

        self.stdout.write(self.style.NOTICE(f"Creating {count} new test users..."))

        for _ in range(count):
            first_name = fake.first_name()
            last_name = fake.last_name()
            email = (
                f"{first_name.lower()}.{last_name.lower()}@{fake.free_email_domain()}"
            )

            if User.objects.filter(email=email).exists():
                self.stdout.write(
                    self.style.WARNING(
                        f"User with email {email} already exists, skipping."
                    )
                )
                continue

            User.objects.create_user(
                email=email,
                password="testpass123",
                first_name=first_name,
                last_name=last_name,
            )
            created_count += 1
            self.stdout.write(self.style.SUCCESS(f"Successfully created user: {email}"))

        self.stdout.write(
            self.style.SUCCESS(
                f"--- All done. Successfully created {created_count} test users. ---"
            )
        )
