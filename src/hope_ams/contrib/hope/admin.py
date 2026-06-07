from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.contrib import admin, messages
from django.http import HttpRequest

from hope_ams.contrib.hope.client import HOPECoreClient

if TYPE_CHECKING:
    from django.db.models import QuerySet


@admin.action(description="Sync all reference data from HOPE Core")
def sync_all_reference_data(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet[Any]) -> None:
    client = HOPECoreClient()
    stats = client.sync_all()
    messages.success(
        request,
        f"Synced {stats.total_business_areas} BAs, {stats.total_programs} programs. "
        f"Errors: {len(stats.errors)}",
    )
    for err in stats.errors:
        messages.warning(request, err)
