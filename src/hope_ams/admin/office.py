from django.contrib import admin
from unfold.admin import ModelAdmin as UnfoldModelAdmin

from hope_ams.admin.sync import SyncAdminMixin, check_hope_connection
from hope_ams.models import Office


@admin.register(Office)
class OfficeAdmin(SyncAdminMixin, UnfoldModelAdmin):  # type: ignore[misc]
    list_display = ["name", "slug", "created_at"]
    search_fields = ["name", "slug"]
    readonly_fields = ["id", "correlation_id", "created_at", "updated_at"]
    actions = [check_hope_connection]
