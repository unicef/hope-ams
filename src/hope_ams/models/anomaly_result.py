from django.db import models
from django.utils.translation import gettext as _

from hope_ams.models.choices import (
    AnomalyStatus,
    Phase,
    SeverityLevel,
)


def get_anomaly_result_severities() -> list[tuple[str, str]]:
    return SeverityLevel.choices


def get_anomaly_result_statuses() -> list[tuple[str, str]]:
    return AnomalyStatus.choices


def get_anomaly_result_object_types() -> list[tuple[str, str]]:
    return [
        ("household", _("Household")),
        ("individual", _("Individual")),
        ("payment", _("Payment")),
        ("payment_plan", _("Payment Plan")),
    ]


def get_anomaly_result_phases() -> list[tuple[str, str]]:
    return Phase.choices


class AnomalyResult(models.Model):
    detection_run = models.ForeignKey(
        "hope_ams.DetectionRun",
        on_delete=models.CASCADE,
        related_name="anomalies",
        verbose_name=_("Detection Run"),
        help_text=_("The detection run this anomaly belongs to"),
    )
    phase = models.CharField(
        verbose_name=_("Phase"),
        max_length=20,
        choices=get_anomaly_result_phases,
        help_text=_("The phase of the detection run (prevention or detection)"),
    )
    rule_name = models.CharField(
        verbose_name=_("Rule Name"),
        max_length=100,
        db_index=True,
        help_text=_("Name of the rule that detected this anomaly"),
    )
    severity = models.CharField(
        verbose_name=_("Severity"),
        max_length=20,
        choices=get_anomaly_result_severities,
        db_index=True,
        help_text=_("Severity level of this anomaly"),
    )
    status = models.CharField(
        verbose_name=_("Status"),
        max_length=20,
        choices=get_anomaly_result_statuses,
        default=AnomalyStatus.OPEN,
        db_index=True,
        help_text=_("Current status of this anomaly"),
    )
    title = models.CharField(
        verbose_name=_("Title"),
        max_length=255,
        help_text=_("Brief title describing the anomaly"),
    )
    description = models.TextField(
        verbose_name=_("Description"),
        blank=True,
        help_text=_("Detailed description of the anomaly"),
    )
    office = models.ForeignKey(
        "hope_ams.Office",
        on_delete=models.CASCADE,
        verbose_name=_("Office"),
        help_text=_("The office where the anomaly was detected"),
    )
    programme = models.ForeignKey(
        "hope_ams.Programme",
        on_delete=models.CASCADE,
        verbose_name=_("Programme"),
        help_text=_("The programme associated with the anomaly"),
    )
    payment_plan = models.ForeignKey(
        "hope_ams.PaymentPlan",
        on_delete=models.CASCADE,
        verbose_name=_("Payment Plan"),
        help_text=_("The payment plan related to this anomaly"),
    )
    object_type = models.CharField(
        verbose_name=_("Object Type"),
        max_length=50,
        choices=get_anomaly_result_object_types,
        help_text=_("Type of object this anomaly relates to"),
    )
    object_id = models.UUIDField(
        verbose_name=_("Object ID"),
        db_index=True,
        help_text=_("Unique identifier for the object"),
    )
    object_unicef_id = models.CharField(
        verbose_name=_("UNICEF ID"),
        max_length=255,
        blank=True,
        help_text=_("UNICEF identifier for the object"),
    )
    metadata = models.JSONField(
        verbose_name=_("Metadata"),
        blank=True,
        default=dict,
        help_text=_("Additional metadata for this anomaly"),
    )
    created_at = models.DateTimeField(
        verbose_name=_("Created At"),
        auto_now_add=True,
        help_text=_("When this anomaly result was created"),
    )
    updated_at = models.DateTimeField(
        verbose_name=_("Updated At"),
        auto_now=True,
        help_text=_("When this anomaly result was last updated"),
    )

    class Meta:
        app_label = "hope_ams"
        verbose_name = _("Anomaly Result")
        verbose_name_plural = _("Anomaly Results")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"[{self.severity}] {self.title}"
