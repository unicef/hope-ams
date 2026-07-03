import contextlib
import uuid
from typing import Any

from django.db import transaction
from rest_framework import serializers

from hope_ams.models import (
    Office,
    Payment,
    PaymentPlan,
    Programme,
)


class OfficeItemSerializer(serializers.Serializer):
    id = serializers.UUIDField()


class ProgrammeItemSerializer(serializers.Serializer):
    id = serializers.UUIDField()


class PaymentPlanPaymentSerializer(serializers.Serializer):
    id = serializers.UUIDField(required=False, default=None)
    individual_id = serializers.CharField(required=False, default="", allow_blank=True)
    currency = serializers.CharField(required=False, default="", allow_blank=True)
    fsp = serializers.CharField(required=False, default="", allow_blank=True)
    delivery_type = serializers.CharField(required=False, default="", allow_blank=True)
    unicef_id = serializers.CharField(required=False, default="", allow_blank=True)
    household_unicef_id = serializers.CharField(required=False, default="", allow_blank=True)
    status = serializers.CharField(required=False, default="", allow_blank=True)
    entitlement_source = serializers.DecimalField(
        max_digits=16, decimal_places=2, required=False, allow_null=True, default=None
    )
    vulnerability_score = serializers.FloatField(required=False, allow_null=True, default=None)
    excluded = serializers.BooleanField(required=False, default=False)
    conflicted = serializers.BooleanField(required=False, default=False)
    order_number = serializers.IntegerField(required=False, allow_null=True, default=None)
    token_number = serializers.CharField(required=False, default="")
    current_household_data = serializers.JSONField(required=False, allow_null=True, default=None)
    entitlement_quantity = serializers.DecimalField(
        max_digits=15, decimal_places=2, required=False, allow_null=True, default=None
    )
    entitlement_quantity_usd = serializers.DecimalField(
        max_digits=15, decimal_places=2, required=False, allow_null=True, default=None
    )
    entitlement_date = serializers.DateTimeField(required=False, allow_null=True, default=None)
    delivered_quantity = serializers.DecimalField(
        max_digits=15, decimal_places=2, required=False, allow_null=True, default=None
    )
    delivered_quantity_usd = serializers.DecimalField(
        max_digits=15, decimal_places=2, required=False, allow_null=True, default=None
    )
    delivery_date_str = serializers.CharField(required=False, allow_null=True, default=None)
    snapshot = serializers.JSONField(required=False, default=dict)
    payment_errors = serializers.JSONField(required=False, default=dict, source="errors")

    def to_internal_value(self, data: dict) -> dict:
        validated = super().to_internal_value(data)

        if "delivery_date_str" in validated and validated.get("delivery_date_str"):
            from datetime import date, datetime

            date_str = validated.pop("delivery_date_str")
            try:
                validated["delivery_date"] = date.fromisoformat(date_str)
            except ValueError, TypeError:
                try:
                    validated["delivery_date"] = datetime.fromisoformat(date_str)
                except ValueError, TypeError:
                    validated["delivery_date"] = None
        else:
            validated.pop("delivery_date_str", None)

        return validated  # type: ignore[no-any-return]


class PaymentPlanSerializer(serializers.Serializer):
    office = OfficeItemSerializer()
    programme = ProgrammeItemSerializer()
    payments = PaymentPlanPaymentSerializer(many=True)
    pk = serializers.UUIDField(required=False, default=None)
    unicef_id = serializers.CharField(required=False, default="")
    status = serializers.CharField(required=False, default="")
    dispersion_start_date = serializers.DateTimeField(required=False, allow_null=True, default=None)
    total_entitled_quantity = serializers.DecimalField(
        max_digits=16, decimal_places=2, required=False, allow_null=True, default=None
    )
    delivery_mechanism = serializers.CharField(required=False, default="")
    financial_service_provider = serializers.CharField(required=False, default="")
    reconciliation_window_in_days = serializers.IntegerField(required=False, allow_null=True, default=None)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._pp_correlation_id: uuid.UUID | None = None

    def to_internal_value(self, data: dict) -> dict:
        pk_raw = data.get("pk") or data.get("correlation_id")
        if pk_raw:
            try:
                self._pp_correlation_id = uuid.UUID(str(pk_raw))
            except ValueError, TypeError:
                self._pp_correlation_id = None
        else:
            self._pp_correlation_id = None

        return super().to_internal_value(data)  # type: ignore[no-any-return]

    def _get_related_object(
        self, model: type[Office | Programme], correlation_id: uuid.UUID, field: str
    ) -> Office | Programme:
        try:
            return model.objects.get(correlation_id=correlation_id)
        except model.DoesNotExist:
            raise serializers.ValidationError(
                {field: f"{model.__name__} with correlation_id {correlation_id!r} does not exist."}
            )

    def create(self, validated_data: dict) -> PaymentPlan:
        office_data = validated_data.pop("office")
        programme_data = validated_data.pop("programme")
        payments_raw = validated_data.pop("payments")

        pp_correlation_id = self._pp_correlation_id or uuid.uuid4()

        office = self._get_related_object(Office, office_data["id"], "office")
        programme = self._get_related_object(Programme, programme_data["id"], "programme")

        with transaction.atomic():
            pp_defaults = {
                "unicef_id": validated_data.pop("unicef_id", ""),
                "status": validated_data.pop("status", ""),
                "dispersion_start_date": validated_data.pop("dispersion_start_date"),
                "currency": validated_data.pop("currency", "USD"),
                "total_entitled_quantity": validated_data.pop("total_entitled_quantity"),
                "delivery_mechanism": validated_data.pop("delivery_mechanism", ""),
                "financial_service_provider": validated_data.pop("financial_service_provider", ""),
                "reconciliation_window_in_days": validated_data.pop("reconciliation_window_in_days"),
                "programme": programme,
                "office": office,
            }
            payment_plan, _ = PaymentPlan.objects.update_or_create(
                correlation_id=pp_correlation_id,
                defaults=pp_defaults,
            )

            payments_to_create = []
            payments_to_update = []
            for p in payments_raw:
                pid = None
                if isinstance(p, dict):
                    pid = p.pop("id", None)
                try:
                    if pid:
                        pid_uuid = uuid.UUID(str(pid)) if not isinstance(pid, uuid.UUID) else pid
                    else:
                        pid_uuid = uuid.uuid4()
                except ValueError, TypeError:
                    pid_uuid = uuid.uuid4()

                # Remove serializer-only fields
                payment_fields = {k: v for k, v in p.items() if k != "id"}
                payment_fields["plan"] = payment_plan
                payment_fields["correlation_id"] = pid_uuid

                existing = None
                with contextlib.suppress(Payment.DoesNotExist):
                    existing = Payment.objects.get(correlation_id=pid_uuid)

                if existing:
                    for k, v in payment_fields.items():
                        setattr(existing, k, v)
                    payments_to_update.append(existing)
                else:
                    payments_to_create.append(Payment(**payment_fields))

            if payments_to_create:
                Payment.objects.bulk_create(payments_to_create, ignore_conflicts=True)
            if payments_to_update:
                for p in payments_to_update:
                    update_fields_list = [f.name for f in p._meta.concrete_fields if not f.primary_key]
                    p.save(update_fields=update_fields_list)

        return payment_plan
