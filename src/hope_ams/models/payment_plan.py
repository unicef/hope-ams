from django.db import models
from django.utils.translation import gettext as _


class PaymentPlan(models.Model):
    correlation_id = models.UUIDField(
        verbose_name=_("Correlation ID"),
        unique=True,
        help_text=_("Unique identifier for this payment plan"),
    )
    unicef_id = models.CharField(
        verbose_name=_("UNICEF ID"),
        max_length=255,
        blank=True,
        db_index=True,
        help_text=_("UNICEF identifier for this payment plan"),
    )
    programme = models.ForeignKey(
        "hope_ams.Programme",
        on_delete=models.CASCADE,
        related_name="payment_plans",
        verbose_name=_("Programme"),
        help_text=_("The programme this payment plan belongs to"),
    )
    office = models.ForeignKey(
        "hope_ams.Office",
        on_delete=models.CASCADE,
        related_name="payment_plans",
        verbose_name=_("Office"),
        help_text=_("The office this payment plan is associated with"),
    )
    status = models.CharField(
        verbose_name=_("Status"),
        max_length=50,
        blank=True,
        default="",
        help_text=_("Current status of the payment plan"),
    )
    dispersion_start_date = models.DateTimeField(
        verbose_name=_("Dispersion Start Date"),
        blank=True,
        null=True,
        help_text=_("Date when dispersion started"),
    )
    currency = models.CharField(
        verbose_name=_("Currency"),
        max_length=3,
        blank=True,
        default="USD",
        help_text=_("Currency code for this payment plan"),
    )
    total_entitled_quantity = models.DecimalField(
        verbose_name=_("Total Entitled Quantity"),
        max_digits=16,
        decimal_places=2,
        blank=True,
        null=True,
        help_text=_("Total quantity entitled in this payment plan"),
    )
    delivery_mechanism = models.CharField(
        verbose_name=_("Delivery Mechanism"),
        max_length=255,
        blank=True,
        help_text=_("Mechanism used for delivering payments"),
    )
    financial_service_provider = models.CharField(
        verbose_name=_("Financial Service Provider"),
        max_length=255,
        blank=True,
        help_text=_("Provider of the financial service"),
    )
    reconciliation_window_in_days = models.IntegerField(
        verbose_name=_("Reconciliation Window (days)"),
        blank=True,
        null=True,
        help_text=_("Number of days for reconciliation window"),
    )
    created_at = models.DateTimeField(
        verbose_name=_("Created At"),
        auto_now_add=True,
        help_text=_("When this payment plan was created"),
    )
    updated_at = models.DateTimeField(
        verbose_name=_("Updated At"),
        auto_now=True,
        help_text=_("When this payment plan was last updated"),
    )

    class Meta:
        app_label = "hope_ams"
        verbose_name = _("Payment Plan")
        verbose_name_plural = _("Payment Plans")

    def __str__(self) -> str:
        return self.unicef_id or str(self.id)
