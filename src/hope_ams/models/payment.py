from django.db import models


class Payment(models.Model):
    plan = models.ForeignKey("hope_ams.PaymentPlan", on_delete=models.CASCADE, related_name="payments")
    correlation_id = models.UUIDField(unique=True)
    individual_id = models.CharField(max_length=255, blank=True, db_index=True)
    currency = models.CharField(max_length=255)
    fsp = models.CharField(max_length=255, help_text="financial service provider")
    delivery_type = models.CharField(max_length=255, help_text="DeliveryMechanism")

    unicef_id = models.CharField(max_length=255, blank=True)
    household_id = models.UUIDField(null=True, blank=True)
    household_unicef_id = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=100, blank=True, default="")
    entitlement_source = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True)
    vulnerability_score = models.FloatField(null=True, blank=True)
    excluded = models.BooleanField(default=False)
    conflicted = models.BooleanField(default=False)
    order_number = models.IntegerField(null=True, blank=True)
    token_number = models.CharField(max_length=255, blank=True)
    current_household_data = models.JSONField(null=True, blank=True)

    entitlement_quantity = models.DecimalField(decimal_places=2, max_digits=15, null=True, blank=True)
    entitlement_quantity_usd = models.DecimalField(decimal_places=2, max_digits=15, null=True, blank=True)
    entitlement_date = models.DateTimeField(null=True, blank=True)
    delivered_quantity = models.DecimalField(decimal_places=2, max_digits=15, null=True, blank=True)
    delivered_quantity_usd = models.DecimalField(decimal_places=2, max_digits=15, null=True, blank=True)
    delivery_date = models.DateTimeField(null=True, blank=True)

    snapshot = models.JSONField(default=dict, blank=True)
    errors = models.JSONField(default=dict, blank=True)

    class Meta:
        app_label = "hope_ams"
        verbose_name = "Payment"
        verbose_name_plural = "Payments"

    def __str__(self) -> str:
        return self.unicef_id or str(self.id)
