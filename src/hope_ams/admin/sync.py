import contextlib
from typing import TYPE_CHECKING, Any

import requests
from admin_extra_buttons.api import button
from admin_extra_buttons.mixins import ExtraButtonsMixin
from django.contrib import admin, messages

from hope_ams.hope_client import HOPEClient

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from django.http import HttpRequest


class SyncAdminMixin(ExtraButtonsMixin):
    @button(
        html_attrs={"class": "aeb-green"},
        change_list=True,
    )
    def sync_from_hope(self, request: "HttpRequest") -> None:
        client = HOPEClient()
        stats = client.sync_all()
        self.message_user(
            request,
            f"Synced {stats.total_offices} offices, {stats.total_programmes} programmes. Errors: {len(stats.errors)}",
            level=messages.SUCCESS,
        )
        for err in stats.errors:
            self.message_user(request, err, level=messages.WARNING)


@admin.action(description="Check connection to HOPE Core API")
def check_hope_connection(
    _modeladmin: admin.ModelAdmin[Any],
    request: "HttpRequest",
    _queryset: "QuerySet[Any]",
) -> None:
    client = HOPEClient()
    try:
        areas = client.get_business_areas()
        count = len(areas)
        names = [a.get("name", "?") for a in areas[:5]]
        extra = f"... and {count - 5} more" if count > 5 else ""
        first_names = ", ".join(names) + " " + str(extra).strip()
        messages.success(request, f"Connected. {count} offices found: {first_names}")
    except requests.exceptions.ConnectionError as e:
        messages.error(request, f"Cannot connect to HOPE Core API at '{client.base_url}': {e}")
    except requests.exceptions.Timeout:
        messages.error(request, f"Timeout connecting to HOPE Core API at '{client.base_url}'")
    except requests.exceptions.HTTPError as e:
        status = getattr(e.response, "status_code", None) or "?"
        body = ""
        with contextlib.suppress(Exception):
            body = e.response.text[:500]
        messages.error(request, f"HOPE Core API returned {status}: {body}")
    except requests.RequestException as e:
        messages.error(
            request,
            f"Unexpected error connecting to HOPE Core API (at '{client.base_url}'): {e}",
        )
    except ValueError as e:
        if "API token" in str(e) or "not defined" in str(e):
            messages.error(request, f"Missing HOPE Core config: {e}")
        else:
            raise
    except Exception as e:  # noqa: BLE001
        messages.error(
            request,
            f"Unexpected error checking HOPE Core connection: {type(e).__name__}: {e}",
        )


@admin.action(description="Sync all reference data from HOPE Core")
def sync_all_reference_data(
    modeladmin: admin.ModelAdmin[Any], request: "HttpRequest", queryset: "QuerySet[Any]"
) -> None:
    client = HOPEClient()
    stats = client.sync_all()
    messages.success(
        request,
        f"Synced {stats.total_offices} offices, {stats.total_programmes} programmes. Errors: {len(stats.errors)}",
    )
    for err in stats.errors:
        messages.warning(request, err)
