from admin_extra_buttons.decorators import button
from django.contrib import admin
from django.http import HttpResponseRedirect, HttpRequest
from django.urls import reverse
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

    @button(
        html_attrs={"class": "aeb-green"},
        change_list=False,
    )
    def dashboard(self, request: "HttpRequest", pk: "str") -> HttpResponseRedirect:
        url = "."
        if prg := self.get_object(request, pk):
            url = reverse("dashboard", args=[prg.office.code, prg.pk])

        return HttpResponseRedirect(url)
