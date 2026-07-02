import uuid

import pytest

from hope_ams.detection.rules.prevention.pregnant_child import PregnantChildRule
from hope_ams.models import (
    AnomalyResult,
    DetectionRun,
    Office,
    PaymentPlan,
    Programme,
    ProgrammeRuleConfiguration,
    RuleConfig,
)


def test_create(db) -> None:
    office = Office.objects.create(correlation_id=uuid.uuid4(), name="Test Office", slug="test-office")
    assert str(office) == "Test Office"


def test_unique_correlation_id(db) -> None:
    uid = uuid.uuid4()
    Office.objects.create(correlation_id=uid, name="Office1", slug="office1")
    with pytest.raises(Exception, match="unique constraint"):
        Office.objects.create(correlation_id=uid, name="Office2", slug="office2")


def test_create_programme(db, business_area: Office) -> None:
    prog = Programme.objects.create(correlation_id=uuid.uuid4(), name="Prog", office=business_area)
    assert str(prog) == "Prog"
    assert prog.office == business_area


def test_create_payment_plan(db, program: Programme, business_area: Office) -> None:
    pp = PaymentPlan.objects.create(
        correlation_id=uuid.uuid4(),
        unicef_id="PP-001",
        programme=program,
        office=business_area,
    )
    assert str(pp) == "PP-001"
    assert pp.programme == program


def test_create_detection_run(db, payment_plan: PaymentPlan, program: Programme, business_area: Office) -> None:
    run = DetectionRun.objects.create(
        phase="prevention",
        trigger="api",
        status="queued",
        payment_plan=payment_plan,
        programme=program,
        office=business_area,
    )
    assert run.status == "queued"
    assert str(run).startswith("prevention run")
    assert run.rules_executed == 0
    assert run.anomalies_found == 0


def test_status_choices(db, payment_plan: PaymentPlan, program: Programme, business_area: Office) -> None:
    for status in ["queued", "running", "completed", "failed"]:
        run = DetectionRun.objects.create(
            phase="prevention",
            trigger="api",
            status=status,
            payment_plan=payment_plan,
            programme=program,
            office=business_area,
        )
        assert run.status == status


def test_create_anomaly_result(db, payment_plan: PaymentPlan, program: Programme, business_area: Office) -> None:
    run = DetectionRun.objects.create(
        phase="prevention",
        trigger="api",
        status="completed",
        payment_plan=payment_plan,
        programme=program,
        office=business_area,
    )
    anomaly = AnomalyResult.objects.create(
        detection_run=run,
        phase="prevention",
        rule_name="pregnant_child",
        severity="critical",
        status="open",
        title="Test anomaly",
        office=business_area,
        programme=program,
        payment_plan=payment_plan,
        object_type="individual",
        object_id=uuid.uuid4(),
    )
    assert str(anomaly) == "[critical] Test anomaly"
    assert anomaly.status == "open"


def test_create_rule_config(db) -> None:
    rc = RuleConfig.objects.create(
        name="test-config",
        rule=PregnantChildRule,
        enabled=True,
        config={"min_age": 12, "max_age": 55},
    )
    assert "pregnant_child" in str(rc)
    assert rc.config == {"min_age": 12, "max_age": 55}


def test_string_representation_rule_config(db) -> None:
    rc = RuleConfig.objects.create(rule=PregnantChildRule, enabled=True)
    assert "pregnant_child" in str(rc)


def test_created_at_set(db) -> None:
    import datetime
    from zoneinfo import ZoneInfo

    rc = RuleConfig.objects.create(rule=PregnantChildRule, enabled=True)
    assert rc.created_at is not None
    diff = datetime.datetime.now(tz=ZoneInfo("UTC")) - rc.created_at
    assert diff.total_seconds() < 60


def test_phase_both(db) -> None:
    rc = RuleConfig.objects.create(rule=PregnantChildRule, enabled=True, phase="both")
    assert str(rc).endswith("(both)")


def test_phase_prevention_only(db) -> None:
    rc = RuleConfig.objects.create(rule=PregnantChildRule, enabled=True, phase="prevention")
    assert rc.phase == "prevention"
    assert str(rc).endswith("(prevention)")


def test_phase_detection_only(db) -> None:
    rc = RuleConfig.objects.create(rule=PregnantChildRule, enabled=True, phase="detection")
    assert rc.phase == "detection"
    assert str(rc).endswith("(detection)")


def test_create_programme_rule_configuration(db, program: Programme) -> None:
    prc = ProgrammeRuleConfiguration.objects.create(
        rule=PregnantChildRule, enabled=True, phase="prevention", programme=program
    )
    assert str(prc) == f"pregnant_child ({program})"


def test_with_config(db, program: Programme) -> None:
    prc = ProgrammeRuleConfiguration.objects.create(
        rule=PregnantChildRule,
        enabled=True,
        phase="prevention",
        programme=program,
        config={"min_age": 12},
    )
    assert prc.config == {"min_age": 12}


def test_programme_specific_takes_precedence(db, program: Programme) -> None:
    from hope_ams.detection.tasks import _load_rule_configs

    RuleConfig.objects.create(rule=PregnantChildRule, enabled=True, phase="both", config={"min_age": 15})
    ProgrammeRuleConfiguration.objects.create(
        rule=PregnantChildRule,
        enabled=True,
        phase="both",
        programme=program,
        config={"min_age": 12},
    )
    result = _load_rule_configs(str(program.correlation_id), "prevention")
    assert PregnantChildRule.name in result
    assert result[PregnantChildRule.name].config["min_age"] == 12
    assert isinstance(result[PregnantChildRule.name], ProgrammeRuleConfiguration)


def test_global_fallback(db, program: Programme) -> None:
    from hope_ams.detection.tasks import _load_rule_configs

    RuleConfig.objects.create(rule=PregnantChildRule, enabled=True, phase="both")
    result = _load_rule_configs(str(program.correlation_id), "prevention")
    assert PregnantChildRule.name in result
    assert isinstance(result[PregnantChildRule.name], RuleConfig)


def test_disabled_excluded_programme_config(db, program: Programme) -> None:
    from hope_ams.detection.tasks import _load_rule_configs

    ProgrammeRuleConfiguration.objects.create(rule=PregnantChildRule, enabled=False, phase="both", programme=program)
    result = _load_rule_configs(str(program.correlation_id), "prevention")
    assert PregnantChildRule.name not in result


def test_wrong_phase_excluded_programme_config(db, program: Programme) -> None:
    from hope_ams.detection.tasks import _load_rule_configs

    ProgrammeRuleConfiguration.objects.create(
        rule=PregnantChildRule, enabled=True, phase="detection", programme=program
    )
    result = _load_rule_configs(str(program.correlation_id), "prevention")
    assert PregnantChildRule.name not in result


if __name__ == "__main__":
    import django
    from django.conf import settings

    if not settings.configured:
        settings.configure(
            DEBUG=True,
            DATABASES={
                "default": {
                    "ENGINE": "django.db.backends.sqlite3",
                    "NAME": ":memory:",
                }
            },
            INSTALLED_APPS=[
                "django.contrib.contenttypes",
                "django.contrib.auth",
                "hope_ams.detection",
            ],
        )
    django.setup()

    import pytest

    pytest.main([__file__, "-v"])
