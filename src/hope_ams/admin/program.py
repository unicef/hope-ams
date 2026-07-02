from django.contrib import admin
from unfold.admin import ModelAdmin as UnfoldModelAdmin

from hope_ams.admin.sync import SyncAdminMixin
from hope_ams.models import Programme, ProgrammeRuleConfiguration


class ProgrammeRuleConfigurationInline(admin.TabularInline):  # type: ignore[type-arg]
    model = ProgrammeRuleConfiguration
    extra = 1
    show_change_link = True
    fields = ["name", "rule", "enabled", "phase"]


@admin.register(Programme)
class ProgrammeAdmin(SyncAdminMixin, UnfoldModelAdmin):  # type: ignore[misc]
    list_display = ["name", "office"]
    search_fields = ["name"]
    autocomplete_fields = ["office"]
    readonly_fields = ["id", "correlation_id", "created_at", "updated_at"]
    inlines = [ProgrammeRuleConfigurationInline]
