from django.contrib import admin

from .models import AnomalyResult, BusinessArea, DetectionRun, PaymentPlan, Program, RuleConfig


@admin.register(BusinessArea)
class BusinessAreaAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "created_at"]
    search_fields = ["name", "slug"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ["name", "business_area"]
    list_filter = ["business_area"]
    search_fields = ["name"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(PaymentPlan)
class PaymentPlanAdmin(admin.ModelAdmin):
    list_display = ["unicef_id", "program", "business_area", "created_at"]
    list_filter = ["business_area", "program"]
    search_fields = ["unicef_id"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(RuleConfig)
class RuleConfigAdmin(admin.ModelAdmin):
    list_display = ["rule_name", "scope", "enabled", "business_area", "program", "payment_plan"]
    list_filter = ["scope", "enabled", "rule_name", "business_area"]
    search_fields = ["rule_name"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(DetectionRun)
class DetectionRunAdmin(admin.ModelAdmin):
    list_display = ["id", "phase", "status", "payment_plan", "rules_executed", "anomalies_found", "started_at"]
    list_filter = ["phase", "status", "business_area"]
    readonly_fields = ["id", "started_at", "finished_at"]


@admin.register(AnomalyResult)
class AnomalyResultAdmin(admin.ModelAdmin):
    list_display = ["title", "severity", "status", "rule_name", "phase", "object_unicef_id", "created_at"]
    list_filter = ["severity", "status", "phase", "rule_name", "business_area"]
    search_fields = ["title", "object_unicef_id"]
    readonly_fields = ["id", "created_at", "updated_at"]
