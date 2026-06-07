from __future__ import annotations

import uuid

from django.db import models


class BusinessArea(models.Model):
    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Business Area"
        verbose_name_plural = "Business Areas"

    def __str__(self) -> str:
        return self.name


class Program(models.Model):
    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=255)
    business_area = models.ForeignKey(BusinessArea, on_delete=models.CASCADE, related_name="programs")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Program"
        verbose_name_plural = "Programs"

    def __str__(self) -> str:
        return self.name


class PaymentPlan(models.Model):
    id = models.UUIDField(primary_key=True)
    unicef_id = models.CharField(max_length=255, blank=True, db_index=True)
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name="payment_plans")
    business_area = models.ForeignKey(BusinessArea, on_delete=models.CASCADE, related_name="payment_plans")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Payment Plan"
        verbose_name_plural = "Payment Plans"

    def __str__(self) -> str:
        return self.unicef_id or str(self.id)


class RuleConfig(models.Model):
    class Scope(models.TextChoices):
        GLOBAL = "global", "Global"
        BUSINESS_AREA = "business_area", "Business Area"
        PROGRAM = "program", "Program"
        PAYMENT_PLAN = "payment_plan", "Payment Plan"

    rule_name = models.CharField(max_length=100, db_index=True)
    enabled = models.BooleanField(default=True)
    config = models.JSONField(default=dict, blank=True)
    scope = models.CharField(max_length=20, choices=Scope.choices)
    business_area = models.ForeignKey(BusinessArea, on_delete=models.CASCADE, null=True, blank=True)
    program = models.ForeignKey(Program, on_delete=models.CASCADE, null=True, blank=True)
    payment_plan = models.ForeignKey(PaymentPlan, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Rule Configuration"
        verbose_name_plural = "Rule Configurations"
        constraints = [
            models.UniqueConstraint(
                fields=["rule_name", "scope", "business_area", "program", "payment_plan"],
                name="unique_rule_config_per_scope",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.rule_name} [{self.scope}]"


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

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phase = models.CharField(max_length=20, choices=Phase.choices)
    trigger = models.CharField(max_length=20, choices=Trigger.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.QUEUED)
    payment_plan = models.ForeignKey(PaymentPlan, on_delete=models.CASCADE, related_name="detection_runs")
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    business_area = models.ForeignKey(BusinessArea, on_delete=models.CASCADE)
    rules_executed = models.IntegerField(default=0)
    anomalies_found = models.IntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "Detection Run"
        verbose_name_plural = "Detection Runs"
        ordering = ["-started_at"]

    def __str__(self) -> str:
        return f"{self.phase} run {self.id} [{self.status}]"


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

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    detection_run = models.ForeignKey(DetectionRun, on_delete=models.CASCADE, related_name="anomalies")
    phase = models.CharField(max_length=20, choices=DetectionRun.Phase.choices)
    rule_name = models.CharField(max_length=100, db_index=True)
    severity = models.CharField(max_length=20, choices=Severity.choices, db_index=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN, db_index=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    business_area = models.ForeignKey(BusinessArea, on_delete=models.CASCADE)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    payment_plan = models.ForeignKey(PaymentPlan, on_delete=models.CASCADE)
    object_type = models.CharField(
        max_length=50,
        choices=[
            ("household", "Household"),
            ("individual", "Individual"),
            ("payment", "Payment"),
            ("payment_plan", "Payment Plan"),
        ],
    )
    object_id = models.UUIDField(db_index=True)
    object_unicef_id = models.CharField(max_length=255, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Anomaly Result"
        verbose_name_plural = "Anomaly Results"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"[{self.severity}] {self.title}"
