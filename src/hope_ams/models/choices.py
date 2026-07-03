from django.db import models
from django.utils.translation import gettext as _


class Phase(models.TextChoices):
    PREVENTION = "prevention", _("Prevention")
    DETECTION = "detection", _("Detection")


class DetectionRunStatus(models.TextChoices):
    QUEUED = "queued", _("Queued")
    RUNNING = "running", _("Running")
    COMPLETED = "completed", _("Completed")
    FAILED = "failed", _("Failed")


class DetectionRunTrigger(models.TextChoices):
    API = "api", _("API")
    MANUAL = "manual", _("Manual")


class SeverityLevel(models.TextChoices):
    LOW = "low", _("Low")
    MEDIUM = "medium", _("Medium")
    HIGH = "high", _("High")
    CRITICAL = "critical", _("Critical")


class AnomalyStatus(models.TextChoices):
    OPEN = "open", _("Open")
    REVIEWING = "reviewing", _("Reviewing")
    DISMISSED = "dismissed", _("Dismissed")
    CONFIRMED = "confirmed", _("Confirmed")
