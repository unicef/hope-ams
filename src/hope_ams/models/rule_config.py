from django.db import models
from strategy_field.fields import StrategyField

from hope_ams.detection.rules.registry import rule_registry


class RuleConfig(models.Model):
    class Phase(models.TextChoices):
        PREVENTION = "prevention", "Prevention"
        DETECTION = "detection", "Detection"
        BOTH = "both", "Both"

    name = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Name",
        help_text="Name of the rule",
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
        help_text="Configuration parameters for this rule",
    )
    phase = models.CharField(
        max_length=20,
        choices=Phase.choices,
        default=Phase.BOTH,
        verbose_name="Phase",
        help_text="Whether this rule applies to prevention or detection phase",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At",
        help_text="When this rule configuration was created",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At",
        help_text="When this rule configuration was last updated",
    )

    class Meta:
        app_label = "hope_ams"
        verbose_name = "Rule Configuration"
        verbose_name_plural = "Rule Configurations"

    def __str__(self) -> str:
        rule_label = self.rule.name if self.rule else "?"
        return f"{rule_label} ({self.phase})"
