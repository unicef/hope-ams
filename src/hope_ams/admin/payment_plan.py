from typing import TYPE_CHECKING

from django.contrib import admin
from unfold.admin import ModelAdmin as UnfoldModelAdmin

if TYPE_CHECKING:
    from django.http import HttpRequest

from hope_ams.models import PaymentPlan


@admin.register(PaymentPlan)
class PaymentPlanAdmin(UnfoldModelAdmin):  # type: ignore[misc]
    list_display = ["unicef_id", "programme", "office", "created_at"]
    list_filter = ["programme"]
    search_fields = ["unicef_id"]
    autocomplete_fields = ["programme", "office"]
    readonly_fields = ["id", "correlation_id", "created_at", "updated_at"]

    def has_add_permission(self, request: "HttpRequest") -> bool:
        return False
