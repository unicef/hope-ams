from django.db import models
from django.utils.translation import gettext as _
from strategy_field.fields import StrategyField

from hope_ams.detection.rules.registry import rule_registry
from hope_ams.models.choices import CommonPhase


def get_programme_rule_config_phases() -> list[tuple[str, str]]:
    return CommonPhase.choices


class ProgrammeRuleConfiguration(models.Model):
    name = models.CharField(
        verbose_name=_("Name"),
        max_length=255,
        blank=True,
        default="",
        help_text=_("Name of the programme rule configuration"),
    )
    rule = StrategyField(
        verbose_name=_("Rule"),
        registry=rule_registry,
        factory=lambda klass, obj: klass(obj),
        blank=True,
        null=True,
        default=None,
        help_text=_("The rule class this configuration applies to"),
    )
    enabled = models.BooleanField(
        verbose_name=_("Enabled"),
        default=True,
        help_text=_("Whether this rule configuration is enabled"),
    )
    config = models.JSONField(
        verbose_name=_("Configuration"),
        blank=True,
        default=dict,
        help_text=_("Configuration parameters for this rule in the programme context"),
    )
    phase = models.CharField(
        verbose_name=_("Phase"),
        max_length=20,
        choices=get_programme_rule_config_phases,
        default=CommonPhase.BOTH,
        help_text=_("Whether this rule applies to prevention or detection phase"),
    )
    programme = models.ForeignKey(
        "hope_ams.Programme",
        on_delete=models.CASCADE,
        related_name="programme_rule_configurations",
        verbose_name=_("Programme"),
        help_text=_("The programme this configuration applies to"),
    )
    created_at = models.DateTimeField(
        verbose_name=_("Created At"),
        auto_now_add=True,
        help_text=_("When this configuration was created"),
    )
    updated_at = models.DateTimeField(
        verbose_name=_("Updated At"),
        auto_now=True,
        help_text=_("When this configuration was last updated"),
    )

    class Meta:
        app_label = "hope_ams"
        verbose_name = _("Programme Rule Configuration")
        verbose_name_plural = _("Programme Rule Configurations")

    def __str__(self) -> str:
        rule_label = self.rule.name if self.rule else "?"
        return f"{rule_label} ({self.programme})"
