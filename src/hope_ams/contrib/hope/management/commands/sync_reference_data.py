from __future__ import annotations

from django.core.management.base import BaseCommand

from hope_ams.contrib.hope.client import HOPECoreClient


class Command(BaseCommand):
    help = "Sync BusinessAreas and Programs from hope-core"

    def handle(self, *args: object, **options: object) -> str | None:
        client = HOPECoreClient()
        stats = client.sync_all()

        self.stdout.write(
            self.style.SUCCESS(
                f"Synced {stats.total_business_areas} business areas "
                f"({stats.business_areas_created} created, {stats.business_areas_updated} updated)"
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Synced {stats.total_programs} programs "
                f"({stats.programs_created} created, {stats.programs_updated} updated)"
            )
        )

        if stats.errors:
            self.stdout.write(self.style.ERROR("Errors:"))
            for err in stats.errors:
                self.stdout.write(self.style.ERROR(f"  - {err}"))

        return None
