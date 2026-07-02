from django.db import models

from hope_ams.models.detection_run import DetectionRun


class AnomalyResult(models.Model):
    class Severity(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        REVIEWING = "reviewing", "Reviewing"
        DISMISSED = "dismissed", "Dismissed"
        CONFIRMED = "confirmed", "Confirmed"

    detection_run = models.ForeignKey(
        "hope_ams.DetectionRun",
        on_delete=models.CASCADE,
        related_name="anomalies",
        verbose_name="Detection Run",
        help_text="The detection run this anomaly belongs to",
    )
    phase = models.CharField(
        max_length=20,
        choices=DetectionRun.Phase.choices,
        verbose_name="Phase",
        help_text="The phase of the detection run (prevention or detection)",
    )
    rule_name = models.CharField(
        max_length=100,
        db_index=True,
        verbose_name="Rule Name",
        help_text="Name of the rule that detected this anomaly",
    )
    severity = models.CharField(
        max_length=20,
        choices=Severity.choices,
        db_index=True,
        verbose_name="Severity",
        help_text="Severity level of this anomaly",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
        db_index=True,
        verbose_name="Status",
        help_text="Current status of this anomaly",
    )
    title = models.CharField(
        max_length=255,
        verbose_name="Title",
        help_text="Brief title describing the anomaly",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Description",
        help_text="Detailed description of the anomaly",
    )
    office = models.ForeignKey(
        "hope_ams.Office",
        on_delete=models.CASCADE,
        verbose_name="Office",
        help_text="The office where the anomaly was detected",
    )
    programme = models.ForeignKey(
        "hope_ams.Programme",
        on_delete=models.CASCADE,
        verbose_name="Programme",
        help_text="The programme associated with the anomaly",
    )
    payment_plan = models.ForeignKey(
        "hope_ams.PaymentPlan",
        on_delete=models.CASCADE,
        verbose_name="Payment Plan",
        help_text="The payment plan related to this anomaly",
    )
    object_type = models.CharField(
        max_length=50,
        choices=[
            ("household", "Household"),
            ("individual", "Individual"),
            ("payment", "Payment"),
            ("payment_plan", "Payment Plan"),
        ],
        verbose_name="Object Type",
        help_text="Type of object this anomaly relates to",
    )
    object_id = models.UUIDField(
        db_index=True,
        verbose_name="Object ID",
        help_text="Unique identifier for the object",
    )
    object_unicef_id = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="UNICEF ID",
        help_text="UNICEF identifier for the object",
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Metadata",
        help_text="Additional metadata for this anomaly",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At",
        help_text="When this anomaly result was created",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At",
        help_text="When this anomaly result was last updated",
    )

    class Meta:
        app_label = "hope_ams"
        verbose_name = "Anomaly Result"
        verbose_name_plural = "Anomaly Results"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"[{self.severity}] {self.title}"
