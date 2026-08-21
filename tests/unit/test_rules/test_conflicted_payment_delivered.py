import uuid

import pytest

from hope_ams.detection.rules.base import RuleContext
from hope_ams.detection.rules.conflicted_payment_delivered import ConflictedPaymentDeliveredRule


@pytest.fixture
def rule():
    return ConflictedPaymentDeliveredRule()


def test_detects_conflicted_delivered(rule, make_pp, make_payment):
    payment = make_payment(conflicted=True, delivered_quantity=500.0)
    ctx = RuleContext(phase="detection", payment_plan=make_pp(), payments=[payment])
    findings = rule.evaluate(ctx)
    assert len(findings) == 1
    assert findings[0].severity == "critical"
    assert findings[0].metadata["delivered_quantity"] == 500.0


def test_no_finding_not_conflicted(rule, make_pp, make_payment):
    payment = make_payment(conflicted=False, delivered_quantity=500.0)
    ctx = RuleContext(phase="detection", payment_plan=make_pp(), payments=[payment])
    assert rule.evaluate(ctx) == []


def test_no_finding_conflicted_not_delivered(rule, make_pp, make_payment):
    payment = make_payment(conflicted=True, delivered_quantity=None)
    ctx = RuleContext(phase="detection", payment_plan=make_pp(), payments=[payment])
    assert rule.evaluate(ctx) == []


def test_no_finding_conflicted_zero_quantity(rule, make_pp, make_payment):
    payment = make_payment(conflicted=True, delivered_quantity=0.0)
    ctx = RuleContext(phase="detection", payment_plan=make_pp(), payments=[payment])
    assert rule.evaluate(ctx) == []


def test_multiple_conflicted_payments(rule, make_pp, make_payment):
    p1 = make_payment(id=uuid.uuid4(), conflicted=True, delivered_quantity=100.0)
    p2 = make_payment(id=uuid.uuid4(), conflicted=True, delivered_quantity=200.0)
    p3 = make_payment(id=uuid.uuid4(), conflicted=False, delivered_quantity=300.0)
    ctx = RuleContext(phase="detection", payment_plan=make_pp(), payments=[p1, p2, p3])
    assert len(rule.evaluate(ctx)) == 2
