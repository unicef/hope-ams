import uuid

import pytest

from hope_ams.detection.rules.base import RuleContext
from hope_ams.detection.rules.missing_budget_commitment import MissingBudgetCommitmentRule


@pytest.fixture
def rule():
    return MissingBudgetCommitmentRule()


def test_detects_none_quantity(rule, make_pp):
    ctx = RuleContext(phase="prevention", payment_plan=make_pp(total_entitled_quantity=None), payments=[])
    findings = rule.evaluate(ctx)
    assert len(findings) == 1
    assert findings[0].object_type == "payment_plan"
    assert findings[0].severity == "medium"


def test_no_finding_when_quantity_set(rule, make_pp):
    ctx = RuleContext(phase="prevention", payment_plan=make_pp(total_entitled_quantity=10000.0), payments=[])
    assert rule.evaluate(ctx) == []


def test_no_finding_when_zero(rule, make_pp):
    ctx = RuleContext(phase="prevention", payment_plan=make_pp(total_entitled_quantity=0.0), payments=[])
    assert rule.evaluate(ctx) == []


def test_finding_has_plan_id(rule, make_pp):
    plan_id = str(uuid.uuid4())
    ctx = RuleContext(phase="prevention", payment_plan=make_pp(id=plan_id, total_entitled_quantity=None), payments=[])
    findings = rule.evaluate(ctx)
    assert str(findings[0].object_id) == plan_id
