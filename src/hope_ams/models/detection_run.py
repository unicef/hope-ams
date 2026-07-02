from django.db import models
from django.utils.translation import gettext as _

from hope_ams.models.choices import (
    DetectionRunPhase,
    DetectionRunStatus,
    DetectionRunTrigger,
)


def get_detection_run_phases() -> list[tuple[str, str]]:
    return DetectionRunPhase.choices


def get_detection_run_statuses() -> list[tuple[str, str]]:
    return DetectionRunStatus.choices


def get_detection_run_triggers() -> list[tuple[str, str]]:
    return DetectionRunTrigger.choices


class DetectionRun(models.Model):
    phase = models.CharField(
        verbose_name=_("Phase"),
        max_length=20,
        choices=get_detection_run_phases,
        help_text=_("The phase of the detection run (prevention or detection)"),
    )
    trigger = models.CharField(
        verbose_name=_("Trigger"),
        max_length=20,
        choices=get_detection_run_triggers,
        help_text=_("How the detection run was triggered"),
    )
    status = models.CharField(
        verbose_name=_("Status"),
        max_length=20,
        choices=get_detection_run_statuses,
        default=DetectionRunStatus.QUEUED,
        help_text=_("Current status of the detection run"),
    )
    payment_plan = models.ForeignKey(
        "hope_ams.PaymentPlan",
        on_delete=models.CASCADE,
        related_name="detection_runs",
        verbose_name=_("Payment Plan"),
        help_text=_("The payment plan this detection run is associated with"),
    )
    programme = models.ForeignKey(
        "hope_ams.Programme",
        on_delete=models.CASCADE,
        verbose_name=_("Programme"),
        help_text=_("The programme this detection run is associated with"),
    )
    office = models.ForeignKey(
        "hope_ams.Office",
        on_delete=models.CASCADE,
        verbose_name=_("Office"),
        help_text=_("The office this detection run is associated with"),
    )
    rules_executed = models.IntegerField(
        verbose_name=_("Rules Executed"),
        default=0,
        help_text=_("Number of rules executed in this detection run"),
    )
    anomalies_found = models.IntegerField(
        verbose_name=_("Anomalies Found"),
        default=0,
        help_text=_("Number of anomalies detected"),
    )
    started_at = models.DateTimeField(
        verbose_name=_("Started At"),
        auto_now_add=True,
        help_text=_("When the detection run started"),
    )
    finished_at = models.DateTimeField(
        verbose_name=_("Finished At"),
        blank=True,
        null=True,
        help_text=_("When the detection run finished"),
    )
    metadata = models.JSONField(
        verbose_name=_("Metadata"),
        blank=True,
        default=dict,
        help_text=_("Additional metadata for this detection run"),
    )

    class Meta:
        app_label = "hope_ams"
        verbose_name = _("Detection Run")
        verbose_name_plural = _("Detection Runs")
        ordering = ["-started_at"]

    def __str__(self) -> str:
        return f"{self.phase} run {self.id} [{self.status}]"
