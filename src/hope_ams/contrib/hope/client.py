from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, cast

import requests
from requests import Response

from hope_ams.config import env
from hope_ams.detections.models import BusinessArea, Program


@dataclass
class SyncStats:
    business_areas_created: int = 0
    business_areas_updated: int = 0
    programs_created: int = 0
    programs_updated: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def total_business_areas(self) -> int:
        return self.business_areas_created + self.business_areas_updated

    @property
    def total_programs(self) -> int:
        return self.programs_created + self.programs_updated


class HOPECoreClient:
    def __init__(self) -> None:
        self.base_url = env("HOPE_CORE_BASE_URL")
        self.token = env("HOPE_CORE_API_TOKEN")

    def _request(self, method: str, path: str) -> Response:
        url = f"{self.base_url.rstrip('/')}{path}"
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.request(method, url, headers=headers, timeout=30)
        response.raise_for_status()
        return response

    def get_business_areas(self) -> list[dict[str, Any]]:
        response = self._request("GET", "/api/rest/business-areas/?active=true")
        data: Any = response.json()
        return cast("list[dict[str, Any]]", data.get("results", data))

    def get_programs(self, business_area_slug: str) -> list[dict[str, Any]]:
        response = self._request(
            "GET", f"/api/rest/business-areas/{business_area_slug}/programs/"
        )
        data: Any = response.json()
        return cast("list[dict[str, Any]]", data.get("results", data))

    def sync_all(self) -> SyncStats:
        stats = SyncStats()

        try:
            ba_list = self.get_business_areas()
        except requests.RequestException as e:
            stats.errors.append(f"Failed to fetch business areas: {e}")
            return stats

        for ba_data in ba_list:
            ba_id = ba_data.get("id")
            ba_name = ba_data.get("name", "")
            ba_slug = ba_data.get("slug", "")
            if not ba_id:
                stats.errors.append("Business area missing id, skipping")
                continue

            _, created = BusinessArea.objects.update_or_create(
                id=ba_id,
                defaults={"name": ba_name, "slug": ba_slug},
            )
            if created:
                stats.business_areas_created += 1
            else:
                stats.business_areas_updated += 1

            try:
                program_list = self.get_programs(ba_slug)
            except requests.RequestException as e:
                stats.errors.append(
                    f"Failed to fetch programs for BA {ba_slug}: {e}"
                )
                continue

            for prog_data in program_list:
                prog_id = prog_data.get("id")
                prog_name = prog_data.get("name", "")
                if not prog_id:
                    stats.errors.append(
                        f"Program in BA {ba_slug} missing id, skipping"
                    )
                    continue

                _, created = Program.objects.update_or_create(
                    id=prog_id,
                    defaults={
                        "name": prog_name,
                        "business_area_id": ba_id,
                    },
                )
                if created:
                    stats.programs_created += 1
                else:
                    stats.programs_updated += 1

        return stats
