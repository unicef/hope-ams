from __future__ import annotations

from typing import TYPE_CHECKING

from django.db.models import Count
from django.shortcuts import render

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse

from .models import AnomalyResult, DetectionRun


def dashboard(request: HttpRequest) -> HttpResponse:
    total_runs = DetectionRun.objects.count()
    total_anomalies = AnomalyResult.objects.count()
    by_severity = dict(
        AnomalyResult.objects.values("severity").annotate(count=Count("id")).values_list("severity", "count")
    )
    by_phase = dict(AnomalyResult.objects.values("phase").annotate(count=Count("id")).values_list("phase", "count"))
    recent_runs = DetectionRun.objects.order_by("-started_at")[:10]

    return render(
        request,
        "detections/dashboard.html",
        {
            "total_runs": total_runs,
            "total_anomalies": total_anomalies,
            "by_severity": by_severity,
            "by_phase": by_phase,
            "recent_runs": recent_runs,
        },
    )


def anomaly_list_view(request: HttpRequest) -> HttpResponse:
    qs = AnomalyResult.objects.select_related("detection_run", "business_area", "program", "payment_plan")
    phase = request.GET.get("phase")
    if phase:
        qs = qs.filter(phase=phase)
    severity = request.GET.get("severity")
    if severity:
        qs = qs.filter(severity=severity)
    status = request.GET.get("status")
    if status:
        qs = qs.filter(status=status)
    qs = qs.order_by("-created_at")

    return render(request, "detections/anomaly_list.html", {"anomalies": qs})
