import pytest

from hope_ams.detection.rules.base import RuleContext
from hope_ams.detection.rules.pregnancy_validity import PregnancyValidityRule


@pytest.fixture
def rule():
    return PregnancyValidityRule()


def test_detects_pregnant_below_min_age(rule, make_pp, make_payment, make_individual):
    ind = make_individual(pregnant=True, birth_date="2015-01-01", sex="F")
    payment = make_payment(snapshot_data={"individuals": [ind]})
    ctx = RuleContext(phase="prevention", payment_plan=make_pp(), payments=[payment])
    findings = rule.evaluate(ctx)
    assert len(findings) == 1
    assert "below minimum age" in findings[0].title
    assert findings[0].severity == "critical"
    assert findings[0].metadata["pregnant"] is True


def test_detects_pregnant_above_max_age(rule, make_pp, make_payment, make_individual):
    ind = make_individual(pregnant=True, birth_date="1960-01-01", sex="F")
    payment = make_payment(snapshot_data={"individuals": [ind]})
    ctx = RuleContext(phase="prevention", payment_plan=make_pp(), payments=[payment])
    findings = rule.evaluate(ctx)
    assert len(findings) == 1
    assert "exceeds maximum age" in findings[0].title


def test_no_finding_pregnant_within_range(rule, make_pp, make_payment, make_individual):
    ind = make_individual(pregnant=True, birth_date="1995-06-15", sex="F")
    payment = make_payment(snapshot_data={"individuals": [ind]})
    ctx = RuleContext(phase="prevention", payment_plan=make_pp(), payments=[payment])
    assert rule.evaluate(ctx) == []


def test_no_finding_not_pregnant(rule, make_pp, make_payment, make_individual):
    ind = make_individual(pregnant=False, birth_date="2015-01-01", sex="F")
    payment = make_payment(snapshot_data={"individuals": [ind]})
    ctx = RuleContext(phase="prevention", payment_plan=make_pp(), payments=[payment])
    assert rule.evaluate(ctx) == []


def test_no_finding_missing_birth_date(rule, make_pp, make_payment, make_individual):
    ind = make_individual(pregnant=True, birth_date=None)
    payment = make_payment(snapshot_data={"individuals": [ind]})
    ctx = RuleContext(phase="prevention", payment_plan=make_pp(), payments=[payment])
    assert rule.evaluate(ctx) == []


def test_no_finding_malformed_birth_date(rule, make_pp, make_payment, make_individual):
    ind = make_individual(pregnant=True, birth_date="not-a-date")
    payment = make_payment(snapshot_data={"individuals": [ind]})
    ctx = RuleContext(phase="prevention", payment_plan=make_pp(), payments=[payment])
    assert rule.evaluate(ctx) == []


def test_respects_custom_min_age(rule, make_pp, make_payment, make_individual):
    # Age ~16 — fine under default min_age=12, flagged if min_age raised to 18
    ind = make_individual(pregnant=True, birth_date="2009-01-01", sex="F")
    payment = make_payment(snapshot_data={"individuals": [ind]})
    ctx = RuleContext(
        phase="prevention",
        payment_plan=make_pp(),
        payments=[payment],
        config={"rules": {"pregnancy_validity": {"config": {"min_age": 18, "max_age": 55}}}},
    )
    findings = rule.evaluate(ctx)
    assert len(findings) == 1
    assert findings[0].metadata["min_age"] == 18


def test_finding_links_individual_and_household(rule, make_pp, make_payment, make_individual):
    ind = make_individual(pregnant=True, birth_date="2015-01-01")
    payment = make_payment(snapshot_data={"individuals": [ind]})
    ctx = RuleContext(phase="prevention", payment_plan=make_pp(), payments=[payment])
    finding = rule.evaluate(ctx)[0]
    assert finding.object_type == "individual"
    assert finding.individual_id == ind["id"]
    assert finding.household_id == payment["household_id"]
