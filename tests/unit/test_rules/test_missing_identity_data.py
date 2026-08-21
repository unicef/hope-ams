import pytest

from hope_ams.detection.rules.base import RuleContext
from hope_ams.detection.rules.missing_identity_data import MissingIdentityDataRule


@pytest.fixture
def rule():
    return MissingIdentityDataRule()


def test_no_finding_complete_individual(rule, make_pp, make_payment, make_individual):
    ind = make_individual()
    payment = make_payment(snapshot_data={"individuals": [ind]})
    ctx = RuleContext(phase="prevention", payment_plan=make_pp(), payments=[payment])
    assert rule.evaluate(ctx) == []


def test_detects_missing_name(rule, make_pp, make_payment, make_individual):
    ind = make_individual(full_name="")
    payment = make_payment(snapshot_data={"individuals": [ind]})
    ctx = RuleContext(phase="prevention", payment_plan=make_pp(), payments=[payment])
    findings = rule.evaluate(ctx)
    assert len(findings) == 1
    assert "full_name" in findings[0].metadata["missing_fields"]


def test_detects_missing_document(rule, make_pp, make_payment, make_individual):
    ind = make_individual(documents=[])
    payment = make_payment(snapshot_data={"individuals": [ind]})
    ctx = RuleContext(phase="prevention", payment_plan=make_pp(), payments=[payment])
    findings = rule.evaluate(ctx)
    assert len(findings) == 1
    assert "document" in findings[0].metadata["missing_fields"]


def test_detects_multiple_missing_fields(rule, make_pp, make_payment, make_individual):
    ind = make_individual(full_name="", birth_date="", documents=[])
    payment = make_payment(snapshot_data={"individuals": [ind]})
    ctx = RuleContext(phase="prevention", payment_plan=make_pp(), payments=[payment])
    findings = rule.evaluate(ctx)
    assert len(findings) == 1
    missing = findings[0].metadata["missing_fields"]
    assert "full_name" in missing
    assert "birth_date" in missing
    assert "document" in missing


def test_require_document_disabled(rule, make_pp, make_payment, make_individual):
    ind = make_individual(documents=[])
    payment = make_payment(snapshot_data={"individuals": [ind]})
    ctx = RuleContext(
        phase="prevention",
        payment_plan=make_pp(),
        payments=[payment],
        config={"rules": {"missing_identity_data": {"config": {"require_document": False}}}},
    )
    assert rule.evaluate(ctx) == []


def test_multiple_individuals_per_payment(rule, make_pp, make_payment, make_individual):
    ind_ok = make_individual()
    ind_bad = make_individual(full_name="", documents=[])
    payment = make_payment(snapshot_data={"individuals": [ind_ok, ind_bad]})
    ctx = RuleContext(phase="prevention", payment_plan=make_pp(), payments=[payment])
    assert len(rule.evaluate(ctx)) == 1


def test_no_individuals_no_finding(rule, make_pp, make_payment):
    payment = make_payment(snapshot_data={"individuals": []})
    ctx = RuleContext(phase="prevention", payment_plan=make_pp(), payments=[payment])
    assert rule.evaluate(ctx) == []
