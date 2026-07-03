from rest_framework import serializers

from hope_ams.models import (
    AnomalyResult,
    DetectionRun,
)
from hope_ams.models.choices import AnomalyStatus


class OfficeItemSerializer(serializers.Serializer):
    id = serializers.UUIDField()


class ProgrammeItemSerializer(serializers.Serializer):
    id = serializers.UUIDField()


class VerificationItemSerializer(serializers.Serializer):
    status = serializers.CharField(required=False, default=None)
    received_amount = serializers.FloatField(required=False, default=None)


class PaymentItemSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    unicef_id = serializers.CharField(required=False, default="")
    household_id = serializers.UUIDField(required=False, default=None)
    household_unicef_id = serializers.CharField(required=False, default="")
    status = serializers.CharField(required=False, default="")
    entitlement_quantity = serializers.FloatField(required=False, default=None)
    entitlement_quantity_usd = serializers.FloatField(required=False, default=None)
    delivered_quantity = serializers.FloatField(required=False, default=None)
    delivered_quantity_usd = serializers.FloatField(required=False, default=None)
    delivery_date = serializers.CharField(required=False, default=None)
    financial_service_provider = serializers.CharField(required=False, default="")
    delivery_type = serializers.CharField(required=False, default="")
    currency = serializers.CharField(required=False, default="")
    excluded = serializers.BooleanField(required=False, default=False)
    conflicted = serializers.BooleanField(required=False, default=False)
    vulnerability_score = serializers.FloatField(required=False, default=None)
    order_number = serializers.IntegerField(required=False, default=None)
    token_number = serializers.CharField(required=False, default="")
    snapshot_data = serializers.JSONField(required=False, default=dict)
    verification = VerificationItemSerializer(required=False, default=None, allow_null=True)
    current_household_data = serializers.JSONField(required=False, default=None, allow_null=True)


class PaymentPlanItemSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    unicef_id = serializers.CharField(required=False, default="")
    office = OfficeItemSerializer()
    programme = ProgrammeItemSerializer()
    status = serializers.CharField(required=False, default="")
    dispersion_start_date = serializers.CharField(required=False, default="")
    currency = serializers.CharField(required=False, default="")
    total_entitled_quantity = serializers.FloatField(required=False, default=0)
    delivery_mechanism = serializers.CharField(required=False, default="")
    financial_service_provider = serializers.CharField(required=False, default="")
    reconciliation_window_in_days = serializers.IntegerField(required=False, default=None)
    payments = PaymentItemSerializer(many=True)


class SubmitRunSerializer(serializers.Serializer):
    phase = serializers.ChoiceField(choices=["prevention", "detection"])
    callback_url = serializers.URLField(required=False, default="")
    payment_plan = PaymentPlanItemSerializer()
    config = serializers.JSONField(required=False, default=dict)


class DetectionRunSerializer(serializers.ModelSerializer):
    office_correlation_id = serializers.UUIDField(source="office.correlation_id", read_only=True)
    programme_correlation_id = serializers.UUIDField(source="programme.correlation_id", read_only=True)
    payment_plan_correlation_id = serializers.UUIDField(source="payment_plan.correlation_id", read_only=True)

    class Meta:
        model = DetectionRun
        fields = [
            "id",
            "phase",
            "trigger",
            "status",
            "payment_plan",
            "programme",
            "office",
            "office_correlation_id",
            "programme_correlation_id",
            "payment_plan_correlation_id",
            "rules_executed",
            "anomalies_found",
            "started_at",
            "finished_at",
            "metadata",
        ]


class AnomalyResultListSerializer(serializers.ModelSerializer):
    office_correlation_id = serializers.UUIDField(source="office.correlation_id", read_only=True)
    programme_correlation_id = serializers.UUIDField(source="programme.correlation_id", read_only=True)
    payment_plan_correlation_id = serializers.UUIDField(source="payment_plan.correlation_id", read_only=True)

    class Meta:
        model = AnomalyResult
        fields = [
            "id",
            "detection_run",
            "phase",
            "rule_name",
            "severity",
            "status",
            "title",
            "description",
            "office",
            "programme",
            "payment_plan",
            "office_correlation_id",
            "programme_correlation_id",
            "payment_plan_correlation_id",
            "object_type",
            "object_id",
            "object_unicef_id",
            "metadata",
            "created_at",
            "updated_at",
        ]


class AnomalyResultStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=AnomalyStatus.choices)


class StatSerializer(serializers.Serializer):
    total_runs = serializers.IntegerField()
    total_anomalies = serializers.IntegerField()
    by_severity = serializers.DictField(child=serializers.IntegerField())
    by_phase = serializers.DictField(child=serializers.IntegerField())
    recent_runs = DetectionRunSerializer(many=True, required=False)
