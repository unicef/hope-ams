from django.db import models
from strategy_field.fields import StrategyField

from hope_ams.detection.rules.registry import rule_registry


class ProgrammeRuleConfiguration(models.Model):
    class Phase(models.TextChoices):
        PREVENTION = "prevention", "Prevention"
        DETECTION = "detection", "Detection"
        BOTH = "both", "Both"

    name = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Name",
        help_text="Name of the programme rule configuration",
    )
    rule = StrategyField(
        registry=rule_registry,
        factory=lambda klass, obj: klass(obj),
        null=True,
        blank=True,
        default=None,
        verbose_name="Rule",
        help_text="The rule class this configuration applies to",
    )
    enabled = models.BooleanField(
        default=True,
        verbose_name="Enabled",
        help_text="Whether this rule configuration is enabled",
    )
    config = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Configuration",
        help_text="Configuration parameters for this rule in the programme context",
    )
    phase = models.CharField(
        max_length=20,
        choices=Phase.choices,
        default=Phase.BOTH,
        verbose_name="Phase",
        help_text="Whether this rule applies to prevention or detection phase",
    )
    programme = models.ForeignKey(
        "hope_ams.Programme",
        on_delete=models.CASCADE,
        related_name="programme_rule_configurations",
        verbose_name="Programme",
        help_text="The programme this configuration applies to",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At",
        help_text="When this configuration was created",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At",
        help_text="When this configuration was last updated",
    )

    class Meta:
        app_label = "hope_ams"
        verbose_name = "Programme Rule Configuration"
        verbose_name_plural = "Programme Rule Configurations"

    def __str__(self) -> str:
        rule_label = self.rule.name if self.rule else "?"
        return f"{rule_label} ({self.programme})"
