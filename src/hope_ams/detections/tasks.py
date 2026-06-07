from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from celery import shared_task
from django.db import transaction

from hope_ams.detections.callback import notify_hope
from hope_ams.detections.models import AnomalyResult, DetectionRun
from hope_ams.detections.rules.base import Finding, RuleContext
from hope_ams.detections.rules.registry import registry

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(Exception,),
)
def process_analysis(task_self: Any, run_id: str, data: dict) -> None:
    run = DetectionRun.objects.get(id=run_id)
    run.status = DetectionRun.Status.RUNNING
    run.save(update_fields=["status"])

    try:
        ctx = RuleContext(
            phase=data["phase"],
            payment_plan=data["payment_plan"],
            payments=data["payment_plan"]["payments"],
            config=data.get("config", {}),
        )

        rule_findings: list[tuple[str, list[Finding]]] = []
        enabled_rules = registry.get_enabled(data["phase"], ctx.config)

        for rule in enabled_rules:
            try:
                findings = rule.evaluate(ctx)
                rule_findings.append((rule.name, findings))
                run.rules_executed += 1
            except Exception:
                logger.exception("Rule %s failed", rule.name)
                run.rules_executed += 1

        with transaction.atomic():
            anomaly_objs = []
            for rule_name, findings in rule_findings:
                anomaly_objs.extend(
                    AnomalyResult(
                        detection_run=run,
                        phase=run.phase,
                        rule_name=rule_name,
                        severity=finding.severity,
                        status=AnomalyResult.Status.OPEN,
                        title=finding.title,
                        description=finding.description,
                        business_area=run.business_area,
                        program=run.program,
                        payment_plan=run.payment_plan,
                        object_type=finding.object_type,
                        object_id=finding.object_id or UUID(int=0),
                        object_unicef_id=finding.object_unicef_id,
                        metadata=finding.metadata,
                    )
                    for finding in findings
                )

            AnomalyResult.objects.bulk_create(anomaly_objs)
            run.anomalies_found = len(anomaly_objs)

        run.status = DetectionRun.Status.COMPLETED
        run.finished_at = datetime.now(tz=UTC)
        run.save()

        callback_url = run.metadata.get("callback_url", "")
        if callback_url:
            notify_hope(
                callback_url,
                {
                    "run_id": str(run.id),
                    "payment_plan_id": str(run.payment_plan_id),
                    "phase": run.phase,
                    "status": "completed",
                    "anomalies_count": run.anomalies_found,
                    "rules_executed": run.rules_executed,
                    "by_severity": _count_by_severity(anomaly_objs),
                },
            )

    except Exception:
        run.status = DetectionRun.Status.FAILED
        run.finished_at = datetime.now(tz=UTC)
        run.save()
        raise


def _count_by_severity(anomalies: list[AnomalyResult]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for a in anomalies:
        counts[a.severity] = counts.get(a.severity, 0) + 1
    return counts
