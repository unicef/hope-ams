from typing import TYPE_CHECKING, Any

from django.contrib import admin
from unfold.admin import ModelAdmin as UnfoldModelAdmin

if TYPE_CHECKING:
    from django.http import HttpRequest

from hope_ams.models import AnomalyResult


@admin.register(AnomalyResult)
class AnomalyResultAdmin(UnfoldModelAdmin):  # type: ignore[misc]
    list_display = [
        "title",
        "severity",
        "display_severity",
        "status",
        "rule_name",
        "phase",
        "object_unicef_id",
        "created_at",
    ]
    list_filter = [
        "severity",
        "status",
        "phase",
        "rule_name",
    ]
    search_fields = ["title", "object_unicef_id"]
    autocomplete_fields = ["detection_run", "office", "programme", "payment_plan"]
    readonly_fields = ["id", "created_at", "updated_at"]

    def display_severity(self, obj: AnomalyResult) -> str:
        return obj.severity

    def get_queryset(self, request: "HttpRequest") -> Any:
        return super().get_queryset(request).select_related("office", "programme", "payment_plan")
