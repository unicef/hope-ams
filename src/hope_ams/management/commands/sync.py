import logging
from typing import Any

from django.core.management import BaseCommand

from hope_ams.hope_client import HOPEClient

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    requires_migrations_checks = False
    requires_system_checks = []

    def handle(self, *args: Any, **options: Any) -> None:
        client = HOPEClient()
        stats = client.sync_all()

        self.stdout.write(
            self.style.SUCCESS(
                f"Synced {stats.total_offices} offices "
                f"({stats.offices_created} created, {stats.offices_updated} updated)"
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Synced {stats.total_programmes} programmes "
                f"({stats.programmes_created} created, {stats.programmes_updated} updated)"
            )
        )

        if stats.errors:
            self.stdout.write(self.style.ERROR("Errors:"))
            for err in stats.errors:
                self.stdout.write(self.style.ERROR(f"  - {err}"))
