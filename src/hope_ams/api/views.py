from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from django.db import transaction
from django.db.models import Count
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from hope_ams.detections.models import (
    AnomalyResult,
    BusinessArea,
    DetectionRun,
    PaymentPlan,
    Program,
    RuleConfig,
)
from hope_ams.detections.tasks import process_analysis

if TYPE_CHECKING:
    from django.http import HttpResponse
    from rest_framework.request import Request

from .auth import APIKeyAuthentication
from .serializers import (
    AnomalyResultListSerializer,
    AnomalyResultStatusSerializer,
    DetectionRunSerializer,
    RuleConfigSerializer,
    StatSerializer,
    SubmitRunSerializer,
)


@api_view(["POST"])
@authentication_classes([APIKeyAuthentication])
@permission_classes([IsAuthenticated])
def submit_run(request: Request) -> HttpResponse:
    serializer = SubmitRunSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    with transaction.atomic():
        ba_data = data["payment_plan"]["business_area"]
        business_area, _ = BusinessArea.objects.update_or_create(
            id=ba_data["id"],
            defaults={"name": ba_data["name"], "slug": ba_data["slug"]},
        )

        prog_data = data["payment_plan"]["program"]
        program, _ = Program.objects.update_or_create(
            id=prog_data["id"],
            defaults={"name": prog_data["name"], "business_area": business_area},
        )

        pp_data = data["payment_plan"]
        payment_plan, _ = PaymentPlan.objects.update_or_create(
            id=pp_data["id"],
            defaults={
                "unicef_id": pp_data.get("unicef_id", ""),
                "program": program,
                "business_area": business_area,
            },
        )

        run = DetectionRun.objects.create(
            phase=data["phase"],
            trigger=DetectionRun.Trigger.API,
            status=DetectionRun.Status.QUEUED,
            payment_plan=payment_plan,
            program=program,
            business_area=business_area,
            metadata={"callback_url": data.get("callback_url", "")},
        )

    process_analysis.delay(str(run.id), serializer.validated_data)

    return Response(
        {"run_id": str(run.id), "status": "queued", "eta_seconds": 30},
        status=status.HTTP_202_ACCEPTED,
    )


@api_view(["GET"])
@authentication_classes([APIKeyAuthentication])
@permission_classes([IsAuthenticated])
def run_detail(request: Request, run_id: str) -> HttpResponse:
    try:
        run = DetectionRun.objects.get(id=run_id)
    except DetectionRun.DoesNotExist:
        return Response({"error": "Run not found"}, status=status.HTTP_404_NOT_FOUND)
    return Response(DetectionRunSerializer(run).data)


@api_view(["GET"])
@authentication_classes([APIKeyAuthentication])
@permission_classes([IsAuthenticated])
def anomaly_list(request: Request) -> HttpResponse:
    qs = AnomalyResult.objects.select_related("detection_run", "business_area", "program", "payment_plan")
    run_id = request.query_params.get("run_id")
    if run_id:
        qs = qs.filter(detection_run_id=UUID(run_id))
    phase = request.query_params.get("phase")
    if phase:
        qs = qs.filter(phase=phase)
    severity = request.query_params.get("severity")
    if severity:
        qs = qs.filter(severity=severity)
    status_param = request.query_params.get("status")
    if status_param:
        qs = qs.filter(status=status_param)
    rule_name = request.query_params.get("rule_name")
    if rule_name:
        qs = qs.filter(rule_name=rule_name)
    ba_id = request.query_params.get("business_area_id")
    if ba_id:
        qs = qs.filter(business_area_id=UUID(ba_id))
    qs = qs.order_by("-created_at")
    page = int(request.query_params.get("page", 1))
    page_size = int(request.query_params.get("page_size", 100))
    start = (page - 1) * page_size
    end = start + page_size
    total = qs.count()
    results = AnomalyResultListSerializer(qs[start:end], many=True).data
    return Response({"count": total, "results": results})


@api_view(["PATCH"])
@authentication_classes([APIKeyAuthentication])
@permission_classes([IsAuthenticated])
def anomaly_update(request: Request, anomaly_id: str) -> HttpResponse:
    try:
        anomaly = AnomalyResult.objects.get(id=anomaly_id)
    except AnomalyResult.DoesNotExist:
        return Response({"error": "Anomaly not found"}, status=status.HTTP_404_NOT_FOUND)
    serializer = AnomalyResultStatusSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    anomaly.status = serializer.validated_data["status"]
    anomaly.save(update_fields=["status", "updated_at"])
    return Response(AnomalyResultListSerializer(anomaly).data)


@api_view(["GET"])
@authentication_classes([APIKeyAuthentication])
@permission_classes([IsAuthenticated])
def stats(request: Request) -> HttpResponse:
    total_runs = DetectionRun.objects.count()
    total_anomalies = AnomalyResult.objects.count()
    by_severity = dict(
        AnomalyResult.objects.values("severity").annotate(count=Count("id")).values_list("severity", "count")
    )
    by_phase = dict(AnomalyResult.objects.values("phase").annotate(count=Count("id")).values_list("phase", "count"))
    recent_runs = DetectionRun.objects.order_by("-started_at")[:10]
    data = {
        "total_runs": total_runs,
        "total_anomalies": total_anomalies,
        "by_severity": by_severity,
        "by_phase": by_phase,
        "recent_runs": DetectionRunSerializer(recent_runs, many=True).data,
    }
    return Response(StatSerializer(data).data)


@api_view(["GET"])
@authentication_classes([APIKeyAuthentication])
@permission_classes([IsAuthenticated])
def rule_config_list(request: Request) -> HttpResponse:
    qs = RuleConfig.objects.select_related("business_area", "program", "payment_plan")
    rule_name = request.query_params.get("rule_name")
    if rule_name:
        qs = qs.filter(rule_name=rule_name)
    scope = request.query_params.get("scope")
    if scope:
        qs = qs.filter(scope=scope)
    return Response(RuleConfigSerializer(qs, many=True).data)
