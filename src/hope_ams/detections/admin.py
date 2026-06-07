from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.contrib import admin
from unfold.admin import ModelAdmin as UnfoldModelAdmin
from unfold.decorators import display

from hope_ams.contrib.hope.admin import sync_all_reference_data
from .models import AnomalyResult, BusinessArea, DetectionRun, PaymentPlan, Program, RuleConfig

if TYPE_CHECKING:
    from django.http import HttpRequest

if TYPE_CHECKING:
    from django.http import HttpRequest


@admin.register(BusinessArea)
class BusinessAreaAdmin(UnfoldModelAdmin):
    list_display = ["name", "slug", "created_at"]
    search_fields = ["name", "slug"]
    readonly_fields = ["id", "created_at", "updated_at"]
    actions = [sync_all_reference_data]


@admin.register(Program)
class ProgramAdmin(UnfoldModelAdmin):
    list_display = ["name", "business_area"]
    list_filter = ["business_area"]
    search_fields = ["name"]
    readonly_fields = ["id", "created_at", "updated_at"]
    actions = [sync_all_reference_data]


@admin.register(PaymentPlan)
class PaymentPlanAdmin(UnfoldModelAdmin):
    list_display = ["unicef_id", "program", "business_area", "created_at"]
    list_filter = ["business_area", "program"]
    search_fields = ["unicef_id"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(RuleConfig)
class RuleConfigAdmin(UnfoldModelAdmin):
    list_display = ["rule_name", "scope", "enabled", "business_area", "program", "payment_plan"]
    list_filter = ["scope", "enabled", "rule_name", "business_area"]
    search_fields = ["rule_name"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(DetectionRun)
class DetectionRunAdmin(UnfoldModelAdmin):
    list_display = ["id", "phase", "status", "payment_plan", "rules_executed", "anomalies_found", "started_at"]
    list_filter = ["phase", "status", "business_area"]
    readonly_fields = ["id", "started_at", "finished_at"]


@admin.register(AnomalyResult)
class AnomalyResultAdmin(UnfoldModelAdmin):
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
        "business_area",
    ]
    search_fields = ["title", "object_unicef_id"]
    readonly_fields = ["id", "created_at", "updated_at"]

    @display(
        description="Severity",
        label=True,
    )
    def display_severity(self, obj: AnomalyResult) -> str:
        return obj.severity

    def get_queryset(self, request: HttpRequest) -> Any:
        return super().get_queryset(request).select_related("business_area", "program", "payment_plan")
