from django.db import models
from django.utils.translation import gettext as _


class Payment(models.Model):
    plan = models.ForeignKey(
        "hope_ams.PaymentPlan",
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name=_("Payment Plan"),
        help_text=_("The payment plan this payment belongs to"),
    )
    correlation_id = models.UUIDField(
        verbose_name=_("Correlation ID"),
        unique=True,
        help_text=_("Unique identifier for this payment"),
    )
    individual_id = models.CharField(
        verbose_name=_("Individual ID"),
        max_length=255,
        blank=True,
        db_index=True,
        help_text=_("Identifier for the individual receiving the payment"),
    )
    currency = models.CharField(
        verbose_name=_("Currency"),
        max_length=255,
        help_text=_("Currency code for this payment"),
    )
    fsp = models.CharField(
        verbose_name=_("Financial Service Provider"),
        max_length=255,
        help_text=_("Financial service provider for this payment"),
    )
    delivery_type = models.CharField(
        verbose_name=_("Delivery Type"),
        max_length=255,
        help_text=_("Delivery mechanism for this payment"),
    )

    unicef_id = models.CharField(
        verbose_name=_("UNICEF ID"),
        max_length=255,
        blank=True,
        help_text=_("UNICEF identifier for this payment"),
    )
    household_id = models.UUIDField(
        verbose_name=_("Household ID"),
        blank=True,
        null=True,
        help_text=_("Unique identifier for the household"),
    )
    household_unicef_id = models.CharField(
        verbose_name=_("Household UNICEF ID"),
        max_length=255,
        blank=True,
        help_text=_("UNICEF identifier for the household"),
    )
    status = models.CharField(
        verbose_name=_("Status"),
        max_length=100,
        blank=True,
        default="",
        help_text=_("Current status of this payment"),
    )
    entitlement_source = models.DecimalField(
        verbose_name=_("Entitlement Source"),
        max_digits=16,
        decimal_places=2,
        blank=True,
        null=True,
        help_text=_("Source amount for this entitlement"),
    )
    vulnerability_score = models.FloatField(
        verbose_name=_("Vulnerability Score"),
        blank=True,
        null=True,
        help_text=_("Vulnerability score for the recipient"),
    )
    excluded = models.BooleanField(
        verbose_name=_("Excluded"),
        default=False,
        help_text=_("Whether this payment is excluded"),
    )
    conflicted = models.BooleanField(
        verbose_name=_("Conflicted"),
        default=False,
        help_text=_("Whether this payment has conflicts"),
    )
    order_number = models.IntegerField(
        verbose_name=_("Order Number"),
        blank=True,
        null=True,
        help_text=_("Order number for this payment"),
    )
    token_number = models.CharField(
        verbose_name=_("Token Number"),
        max_length=255,
        blank=True,
        help_text=_("Token number for this payment"),
    )
    current_household_data = models.JSONField(
        verbose_name=_("Current Household Data"),
        blank=True,
        null=True,
        help_text=_("Current data associated with the household"),
    )

    entitlement_quantity = models.DecimalField(
        verbose_name=_("Entitlement Quantity"),
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        help_text=_("Quantity entitled for this payment"),
    )
    entitlement_quantity_usd = models.DecimalField(
        verbose_name=_("Entitlement Quantity (USD)"),
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        help_text=_("Entitlement quantity in USD"),
    )
    entitlement_date = models.DateTimeField(
        verbose_name=_("Entitlement Date"),
        blank=True,
        null=True,
        help_text=_("Date when entitlement was set"),
    )
    delivered_quantity = models.DecimalField(
        verbose_name=_("Delivered Quantity"),
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        help_text=_("Quantity actually delivered"),
    )
    delivered_quantity_usd = models.DecimalField(
        verbose_name=_("Delivered Quantity (USD)"),
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        help_text=_("Delivered quantity in USD"),
    )
    delivery_date = models.DateTimeField(
        verbose_name=_("Delivery Date"),
        blank=True,
        null=True,
        help_text=_("Date when payment was delivered"),
    )

    snapshot = models.JSONField(
        verbose_name=_("Snapshot"),
        blank=True,
        default=dict,
        help_text=_("Snapshot of data at time of processing"),
    )
    errors = models.JSONField(
        verbose_name=_("Errors"),
        blank=True,
        default=dict,
        help_text=_("Errors encountered during processing"),
    )

    class Meta:
        app_label = "hope_ams"
        verbose_name = _("Payment")
        verbose_name_plural = _("Payments")

    def __str__(self) -> str:
        return self.unicef_id or str(self.id)
