from django.db import models


class PaymentPlan(models.Model):
    correlation_id = models.UUIDField(
        unique=True,
        verbose_name="Correlation ID",
        help_text="Unique identifier for this payment plan",
    )
    unicef_id = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name="UNICEF ID",
        help_text="UNICEF identifier for this payment plan",
    )
    programme = models.ForeignKey(
        "hope_ams.Programme",
        on_delete=models.CASCADE,
        related_name="payment_plans",
        verbose_name="Programme",
        help_text="The programme this payment plan belongs to",
    )
    office = models.ForeignKey(
        "hope_ams.Office",
        on_delete=models.CASCADE,
        related_name="payment_plans",
        verbose_name="Office",
        help_text="The office this payment plan is associated with",
    )
    status = models.CharField(
        max_length=50,
        blank=True,
        default="",
        verbose_name="Status",
        help_text="Current status of the payment plan",
    )
    dispersion_start_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Dispersion Start Date",
        help_text="Date when dispersion started",
    )
    currency = models.CharField(
        max_length=3,
        blank=True,
        default="USD",
        verbose_name="Currency",
        help_text="Currency code for this payment plan",
    )
    total_entitled_quantity = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Total Entitled Quantity",
        help_text="Total quantity entitled in this payment plan",
    )
    delivery_mechanism = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Delivery Mechanism",
        help_text="Mechanism used for delivering payments",
    )
    financial_service_provider = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Financial Service Provider",
        help_text="Provider of the financial service",
    )
    reconciliation_window_in_days = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Reconciliation Window (days)",
        help_text="Number of days for reconciliation window",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At",
        help_text="When this payment plan was created",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At",
        help_text="When this payment plan was last updated",
    )

    class Meta:
        app_label = "hope_ams"
        verbose_name = "Payment Plan"
        verbose_name_plural = "Payment Plans"

    def __str__(self) -> str:
        return self.unicef_id or str(self.id)
