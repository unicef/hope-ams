from typing import TYPE_CHECKING

from django.db.models import Count
from django.shortcuts import render

from hope_ams.models import AnomalyResult, DetectionRun

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse


def dashboard(request: "HttpRequest", office: str, program: int) -> "HttpResponse":
    base_runs = DetectionRun.objects.all()
    base_anomalies = AnomalyResult.objects.all()

    total_runs = base_runs.count()
    total_anomalies = base_anomalies.count()
    by_severity = dict(base_anomalies.values("severity").annotate(count=Count("id")).values_list("severity", "count"))
    by_phase = dict(base_anomalies.values("phase").annotate(count=Count("id")).values_list("phase", "count"))
    recent_runs = base_runs.order_by("-started_at")[:10]

    return render(
        request,
        "detection/dashboard.html",
        {
            "total_runs": total_runs,
            "total_anomalies": total_anomalies,
            "by_severity": by_severity,
            "by_phase": by_phase,
            "recent_runs": recent_runs,
        },
    )


def anomaly_list_view(request: "HttpRequest") -> "HttpResponse":
    qs = AnomalyResult.objects.select_related("detection_run", "office", "programme", "payment_plan").order_by(
        "-created_at"
    )
    phase = request.GET.get("phase")
    if phase:
        qs = qs.filter(phase=phase)
    severity = request.GET.get("severity")
    if severity:
        qs = qs.filter(severity=severity)
    status = request.GET.get("status")
    if status:
        qs = qs.filter(status=status)

    return render(request, "detection/anomaly_list.html", {"anomalies": qs})
