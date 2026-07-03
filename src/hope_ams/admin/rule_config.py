import enum
from typing import TYPE_CHECKING

from admin_extra_buttons.decorators import button
from admin_extra_buttons.mixins import ExtraButtonsMixin
from django.contrib import admin
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin as UnfoldModelAdmin

from hope_ams.models import RuleConfig

if TYPE_CHECKING:
    from hope_ams.detection.rules.base import RuleConfigForm


class ButtonColor(enum.Enum):
    ACTION = "aeb-green"
    DANGER = "aeb-danger"
    WARN = "aeb-warn"


@admin.register(RuleConfig)
class RuleConfigAdmin(ExtraButtonsMixin, UnfoldModelAdmin):  # type: ignore[misc]
    list_display = [
        "name",
        "display_rule",
        "phase",
        "enabled",
    ]
    list_filter = ["phase", "enabled", "rule"]
    search_fields = ["name"]

    def display_rule(self, obj: RuleConfig) -> str:
        return str(obj.rule) if obj.rule else "—"

    change_form_template = "admin/detection/ruleconfig/change_form.html"
    exclude = ["config"]
    readonly_fields = ["created_at", "updated_at"]

    @button(
        html_attrs={"class": ButtonColor.ACTION.value},
        change_form=True,
    )
    def configure(self, request: HttpRequest, pk: str) -> HttpResponse:
        obj: RuleConfig | None = self.get_object(request, pk)
        if obj is None:
            raise Http404
        context = self.get_common_context(request, pk, action_title=_("Configure rule"))
        form_class: type[RuleConfigForm] | None = obj.rule.config_class if obj.rule else None

        if form_class:
            if request.method == "POST":
                config_form = form_class(request.POST)
                if config_form.is_valid():
                    obj.config = config_form.cleaned_data
                    obj.save(update_fields=["config"])
                    self.message_user(request, _("Rule %(name)s configured") % {"name": obj.name})
                    return redirect(reverse("admin:hope_ams_ruleconfig_change", args=(obj.pk,)))
            else:
                initial = dict(obj.rule.default_config) if obj.rule else {}
                initial.update(obj.config)
                config_form = form_class(initial=initial)

            fs = [("", {"fields": list(form_class.declared_fields.keys())})]
            from unfold.forms import AdminForm

            context["adminform"] = AdminForm(config_form, fs, {}, model_admin=self)
        else:
            context["no_config"] = True

        return TemplateResponse(request, "admin/detection/ruleconfig/configure.html", context)
