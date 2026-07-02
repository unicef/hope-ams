from dataclasses import dataclass, field
from typing import Any, cast

import requests
from django.conf import settings
from requests import Response

from hope_ams.models import Office, Programme


@dataclass
class SyncStats:
    offices_created: int = 0
    offices_updated: int = 0
    programmes_created: int = 0
    programmes_updated: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def total_offices(self) -> int:
        return self.offices_created + self.offices_updated

    @property
    def total_programmes(self) -> int:
        return self.programmes_created + self.programmes_updated


class HOPEClient:
    def __init__(self) -> None:
        self.base_url = settings.HOPE_API_URL
        self.token = settings.HOPE_API_TOKEN

    def _request(self, method: str, path: str) -> Response:
        url = f"{self.base_url.rstrip('/')}{path}"
        headers = {"Authorization": f"Token {self.token}"}
        response = requests.request(method, url, headers=headers, timeout=30)
        response.raise_for_status()
        return response

    def get_business_areas(self) -> list[dict[str, Any]]:
        response = self._request("GET", "/business-areas/?active=true")
        data: Any = response.json()
        return cast("list[dict[str, Any]]", data.get("results", data))

    def get_programs(self) -> list[dict[str, Any]]:
        response = self._request("GET", "/programs/")
        data: Any = response.json()
        return cast("list[dict[str, Any]]", data.get("results", data))

    def _sync_offices(self, stats: SyncStats) -> dict[str, Office]:
        ba_list = self.get_business_areas()
        ba_by_code: dict[str, Office] = {}
        for ba_data in ba_list:
            ba_id = ba_data.get("id")
            ba_name = ba_data.get("name", "")
            ba_slug = ba_data.get("slug", "")
            ba_code = ba_data.get("business_area_code") or ba_data.get("code") or ""
            if not ba_id:
                stats.errors.append("Business area missing id, skipping")
                continue

            office, created = Office.objects.update_or_create(
                correlation_id=ba_id,
                defaults={"name": ba_name, "slug": ba_slug, "code": ba_code},
            )
            if created:
                stats.offices_created += 1
            else:
                stats.offices_updated += 1
            if ba_code:
                ba_by_code[ba_code] = office
        return ba_by_code

    def _sync_programs(self, stats: SyncStats, ba_by_code: dict[str, Office]) -> None:
        program_list = self.get_programs()
        for prog_data in program_list:
            prog_id = prog_data.get("id")
            prog_name = prog_data.get("name", "")
            if not prog_id:
                stats.errors.append("Program missing id, skipping")
                continue

            ba_code = prog_data.get("business_area_code") or ""
            office = ba_by_code.get(ba_code)
            if not office:
                stats.errors.append(f"Office not found for program {prog_id} (business_area_code={ba_code})")
                continue

            _, created = Programme.objects.update_or_create(
                correlation_id=prog_id,
                defaults={
                    "name": prog_name,
                    "office": office,
                },
            )
            if created:
                stats.programmes_created += 1
            else:
                stats.programmes_updated += 1

    def sync_all(self) -> SyncStats:
        stats = SyncStats()

        try:
            ba_by_code = self._sync_offices(stats)
        except requests.RequestException as e:
            stats.errors.append(f"Failed to fetch business areas: {e}")
            return stats

        try:
            self._sync_programs(stats, ba_by_code)
        except requests.RequestException as e:
            stats.errors.append(f"Failed to fetch programs: {e}")

        return stats
