import uuid
from unittest.mock import patch

import pytest
from testutils.factories import RuleConfigFactory

from hope_ams.detection.tasks import _load_rule_configs
from hope_ams.models import ProgrammeRuleConfiguration
from hope_ams.models.choices import DetectionRunStatus

pytestmark = [pytest.mark.django_db]


def test_global_config(business_area, program) -> None:
    rc = RuleConfigFactory(phase="prevention")
    result = _load_rule_configs(str(program.correlation_id), "prevention")
    assert rc.rule.name in result


def test_programme_config(business_area, program) -> None:
    from hope_ams.detection.rules.pregnancy_validity import PregnancyValidityRule

    prc = ProgrammeRuleConfiguration.objects.create(
        rule=PregnancyValidityRule, phase="prevention", programme=program, enabled=True
    )
    result = _load_rule_configs(str(program.correlation_id), "prevention")
    assert prc.rule.name in result


def test_wrong_phase_excluded(business_area, program) -> None:
    from hope_ams.detection.rules.pregnancy_validity import PregnancyValidityRule

    ProgrammeRuleConfiguration.objects.create(
        rule=PregnancyValidityRule, phase="detection", programme=program, enabled=True
    )
    result = _load_rule_configs(str(program.correlation_id), "prevention")
    assert len(result) == 0


def test_disabled_excluded(business_area, program) -> None:
    from hope_ams.detection.rules.pregnancy_validity import PregnancyValidityRule

    ProgrammeRuleConfiguration.objects.create(
        rule=PregnancyValidityRule, phase="prevention", programme=program, enabled=False
    )
    result = _load_rule_configs(str(program.correlation_id), "prevention")
    assert len(result) == 0


def test_programme_not_found() -> None:
    result = _load_rule_configs(str(uuid.uuid4()), "prevention")
    assert len(result) == 0


@patch("hope_ams.detection.tasks.notify_hope")
def test_process_analysis_no_rules(mock_notify, payment_plan, sample_submit_payload) -> None:
    from hope_ams.detection.tasks import process_analysis
    from hope_ams.models import DetectionRun

    run = DetectionRun.objects.create(
        phase="prevention",
        trigger="api",
        status="queued",
        payment_plan=payment_plan,
        programme=payment_plan.programme,
        office=payment_plan.office,
    )

    process_analysis.__wrapped__(run.id, sample_submit_payload)

    run.refresh_from_db()
    assert run.status == DetectionRunStatus.COMPLETED
    assert run.rules_executed == 0
    assert run.anomalies_found == 0


@patch("hope_ams.detection.tasks.notify_hope")
def test_process_analysis_with_callback(mock_notify, payment_plan, sample_submit_payload) -> None:
    from hope_ams.detection.tasks import process_analysis
    from hope_ams.models import DetectionRun

    payload = {**sample_submit_payload, "callback_url": "https://example.com/callback/"}
    run = DetectionRun.objects.create(
        phase="prevention",
        trigger="api",
        status="queued",
        payment_plan=payment_plan,
        programme=payment_plan.programme,
        office=payment_plan.office,
        metadata={"callback_url": "https://example.com/callback/"},
    )

    process_analysis.__wrapped__(run.id, payload)

    run.refresh_from_db()
    assert run.status == DetectionRunStatus.COMPLETED
    mock_notify.assert_called_once()


@patch("hope_ams.detection.tasks.notify_hope")
def test_process_analysis_with_rules(mock_notify, payment_plan, sample_payments) -> None:
    from hope_ams.detection.tasks import process_analysis
    from hope_ams.models import DetectionRun

    payload = {
        "phase": "prevention",
        "config": {"rules": {}},
        "payment_plan": {
            "id": str(payment_plan.correlation_id),
            "unicef_id": payment_plan.unicef_id,
            "office": {
                "id": str(payment_plan.office.correlation_id),
                "name": "Office",
                "slug": "office",
            },
            "programme": {
                "id": str(payment_plan.programme.correlation_id),
                "name": "P1",
            },
            "status": "locked",
            "currency": "USD",
            "total_entitled_quantity": 10000.0,
            "payments": sample_payments,
        },
    }
    run = DetectionRun.objects.create(
        phase="prevention",
        trigger="api",
        status="queued",
        payment_plan=payment_plan,
        programme=payment_plan.programme,
        office=payment_plan.office,
    )

    process_analysis.__wrapped__(run.id, payload)

    run.refresh_from_db()
    assert run.status == DetectionRunStatus.COMPLETED


def test_process_analysis_failure(payment_plan, sample_submit_payload) -> None:
    from hope_ams.detection.tasks import process_analysis
    from hope_ams.models import DetectionRun

    run = DetectionRun.objects.create(
        phase="prevention",
        trigger="api",
        status="queued",
        payment_plan=payment_plan,
        programme=payment_plan.programme,
        office=payment_plan.office,
    )

    with patch("hope_ams.detection.tasks.rule_registry.get_all", side_effect=ValueError("boom")):
        with pytest.raises(ValueError, match="boom"):
            process_analysis.__wrapped__(run.id, sample_submit_payload)

    run.refresh_from_db()
    assert run.status == DetectionRunStatus.FAILED
