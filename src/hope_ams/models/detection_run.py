from django.db import models


class DetectionRun(models.Model):
    class Phase(models.TextChoices):
        PREVENTION = "prevention", "Prevention"
        DETECTION = "detection", "Detection"

    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"
        RUNNING = "running", "Running"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    class Trigger(models.TextChoices):
        API = "api", "API"
        MANUAL = "manual", "Manual"

    phase = models.CharField(
        max_length=20,
        choices=Phase.choices,
        verbose_name="Phase",
        help_text="The phase of the detection run (prevention or detection)",
    )
    trigger = models.CharField(
        max_length=20,
        choices=Trigger.choices,
        verbose_name="Trigger",
        help_text="How the detection run was triggered",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.QUEUED,
        verbose_name="Status",
        help_text="Current status of the detection run",
    )
    payment_plan = models.ForeignKey(
        "hope_ams.PaymentPlan",
        on_delete=models.CASCADE,
        related_name="detection_runs",
        verbose_name="Payment Plan",
        help_text="The payment plan this detection run is associated with",
    )
    programme = models.ForeignKey(
        "hope_ams.Programme",
        on_delete=models.CASCADE,
        verbose_name="Programme",
        help_text="The programme this detection run is associated with",
    )
    office = models.ForeignKey(
        "hope_ams.Office",
        on_delete=models.CASCADE,
        verbose_name="Office",
        help_text="The office this detection run is associated with",
    )
    rules_executed = models.IntegerField(
        default=0,
        verbose_name="Rules Executed",
        help_text="Number of rules executed in this detection run",
    )
    anomalies_found = models.IntegerField(
        default=0,
        verbose_name="Anomalies Found",
        help_text="Number of anomalies detected",
    )
    started_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Started At",
        help_text="When the detection run started",
    )
    finished_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Finished At",
        help_text="When the detection run finished",
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Metadata",
        help_text="Additional metadata for this detection run",
    )

    class Meta:
        app_label = "hope_ams"
        verbose_name = "Detection Run"
        verbose_name_plural = "Detection Runs"
        ordering = ["-started_at"]

    def __str__(self) -> str:
        return f"{self.phase} run {self.id} [{self.status}]"
