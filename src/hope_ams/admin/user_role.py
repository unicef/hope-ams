from django.contrib import admin
from unfold.admin import ModelAdmin as UnfoldModelAdmin

from hope_ams.models import UserRole


@admin.register(UserRole)
class UserRoleAdmin(UnfoldModelAdmin):  # type: ignore[misc]
    list_display = ["user", "country_office", "group", "expires"]
    list_filter = ["expires"]
    search_fields = ["user__username", "country_office__name"]
    autocomplete_fields = ["user", "country_office", "group", "programme"]
