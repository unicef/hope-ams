import logging
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from celery import shared_task
from django.db import transaction

from hope_ams.detection.callback import notify_hope
from hope_ams.detection.rules.base import Finding, RuleContext
from hope_ams.detection.rules.registry import rule_registry
from hope_ams.models import (
    AnomalyResult,
    DetectionRun,
    Programme,
    ProgrammeRuleConfiguration,
    RuleConfig,
)
from hope_ams.models.choices import AnomalyStatus, DetectionRunStatus

logger = logging.getLogger(__name__)


def _load_rule_configs(programme_id: str, phase: str) -> dict[str, RuleConfig | ProgrammeRuleConfiguration]:
    """Return enabled configs for the given programme that match the phase.

    ProgrammeRuleConfiguration (programme-specific) takes precedence over
    RuleConfig (global) for the same rule name.
    """
    try:
        programme_pk = Programme.objects.values_list("id", flat=True).get(correlation_id=programme_id)
    except Programme.DoesNotExist:
        return {}

    configs: dict[str, RuleConfig | ProgrammeRuleConfiguration] = {}

    for rc in RuleConfig.objects.all():
        if not rc.enabled:
            continue
        if rc.phase != phase:
            continue
        configs[rc.rule.name] = rc

    for prc in ProgrammeRuleConfiguration.objects.filter(programme_id=programme_pk):
        if not prc.enabled:
            continue
        if prc.phase != phase:
            continue
        configs[prc.rule.name] = prc

    return configs


@shared_task(  # type: ignore[untyped-decorator]
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(Exception,),
)
def process_analysis(task_self: Any, run_id: int, data: dict[str, Any]) -> None:
    run = DetectionRun.objects.get(id=run_id)
    run.status = DetectionRunStatus.RUNNING
    run.save(update_fields=["status"])

    try:
        ctx = RuleContext(
            phase=data["phase"],
            payment_plan=data["payment_plan"],
            payments=data["payment_plan"]["payments"],
            config=data.get("config", {}),
        )

        db_configs = _load_rule_configs(ctx.programme_id, data["phase"])

        rule_findings: list[tuple[str, list[Finding]]] = []
        all_phase_rules = rule_registry.get_all(data["phase"])

        for rule in all_phase_rules:
            if rule.name not in db_configs:
                api_rule_cfg = ctx.config.get("rules", {}).get(rule.name, {})
                if not api_rule_cfg.get("enabled", False):
                    continue
            else:
                rule.rule_config = db_configs[rule.name]  # type: ignore[assignment]
                api_rule_cfg = ctx.config.get("rules", {}).get(rule.name, {})
                if not api_rule_cfg.get("enabled", True):
                    continue
            try:
                findings = rule.evaluate(ctx)
                rule_findings.append((rule.name, findings))
                run.rules_executed += 1
            except Exception:
                logger.exception("Rule %s failed", rule.name)
                run.rules_executed += 1

        with transaction.atomic():
            anomaly_objs: list[AnomalyResult] = []
            for rule_name, findings in rule_findings:
                anomaly_objs.extend(
                    AnomalyResult(
                        detection_run=run,
                        phase=run.phase,
                        rule_name=rule_name,
                        severity=finding.severity,
                        status=AnomalyStatus.OPEN,
                        title=finding.title,
                        description=finding.description,
                        office=run.office,
                        programme=run.programme,
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

        run.status = DetectionRunStatus.COMPLETED
        run.finished_at = datetime.now(tz=UTC)
        run.save()

        callback_url = run.metadata.get("callback_url", "")
        if callback_url:
            notify_hope(
                callback_url,
                {
                    "run_id": str(run.id),
                    "payment_plan_id": str(run.payment_plan.correlation_id),
                    "phase": run.phase,
                    "status": "completed",
                    "anomalies_count": run.anomalies_found,
                    "rules_executed": run.rules_executed,
                    "by_severity": _count_by_severity(anomaly_objs),
                },
            )

    except Exception:
        run.status = DetectionRunStatus.FAILED
        run.finished_at = datetime.now(tz=UTC)
        run.save()
        raise


def _count_by_severity(anomalies: list[AnomalyResult]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for a in anomalies:
        counts[a.severity] = counts.get(a.severity, 0) + 1
    return counts
