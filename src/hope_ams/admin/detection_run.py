from django.contrib import admin
from unfold.admin import ModelAdmin as UnfoldModelAdmin

from hope_ams.models import DetectionRun


@admin.register(DetectionRun)
class DetectionRunAdmin(UnfoldModelAdmin):  # type: ignore[misc]
    list_display = [
        "id",
        "phase",
        "status",
        "payment_plan",
        "rules_executed",
        "anomalies_found",
        "started_at",
    ]
    list_filter = ["phase", "status"]
    search_fields = ["id"]
    autocomplete_fields = ["payment_plan", "programme", "office"]
    readonly_fields = ["id", "started_at", "finished_at"]
