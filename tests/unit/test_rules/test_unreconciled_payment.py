from datetime import UTC, datetime, timedelta

import pytest

from hope_ams.detection.rules.base import RuleContext
from hope_ams.detection.rules.unreconciled_payment import UnreconciledPaymentRule


def stale_date(days=40):
    return (datetime.now(tz=UTC) - timedelta(days=days)).isoformat()


def recent_date(days=5):
    return (datetime.now(tz=UTC) - timedelta(days=days)).isoformat()


@pytest.fixture
def rule():
    return UnreconciledPaymentRule()


def test_detects_stale_undelivered_payment(rule, make_pp, make_payment):
    payment = make_payment(delivery_date=stale_date(40))
    ctx = RuleContext(phase="detection", payment_plan=make_pp(), payments=[payment])
    findings = rule.evaluate(ctx)
    assert len(findings) == 1
    assert findings[0].object_type == "payment"
    assert findings[0].metadata["reconciliation_window"] == 30


def test_no_finding_when_delivered(rule, make_pp, make_payment):
    payment = make_payment(delivery_date=stale_date(40), delivered_quantity=500.0)
    ctx = RuleContext(phase="detection", payment_plan=make_pp(), payments=[payment])
    assert rule.evaluate(ctx) == []


def test_no_finding_when_excluded(rule, make_pp, make_payment):
    payment = make_payment(delivery_date=stale_date(40), excluded=True)
    ctx = RuleContext(phase="detection", payment_plan=make_pp(), payments=[payment])
    assert rule.evaluate(ctx) == []


def test_no_finding_when_recent(rule, make_pp, make_payment):
    payment = make_payment(delivery_date=recent_date(5))
    ctx = RuleContext(phase="detection", payment_plan=make_pp(), payments=[payment])
    assert rule.evaluate(ctx) == []


def test_no_finding_when_no_date(rule, make_pp, make_payment):
    payment = make_payment()
    ctx = RuleContext(phase="detection", payment_plan=make_pp(), payments=[payment])
    assert rule.evaluate(ctx) == []


def test_falls_back_to_entitlement_date(rule, make_pp, make_payment):
    payment = make_payment(entitlement_date=stale_date(40))
    ctx = RuleContext(phase="detection", payment_plan=make_pp(), payments=[payment])
    assert len(rule.evaluate(ctx)) == 1


def test_respects_plan_reconciliation_window(rule, make_pp, make_payment):
    payment = make_payment(delivery_date=stale_date(10))
    ctx = RuleContext(phase="detection", payment_plan=make_pp(reconciliation_window_in_days=5), payments=[payment])
    findings = rule.evaluate(ctx)
    assert len(findings) == 1
    assert findings[0].metadata["reconciliation_window"] == 5


def test_invalid_date_skipped(rule, make_pp, make_payment):
    payment = make_payment(delivery_date="not-a-date")
    ctx = RuleContext(phase="detection", payment_plan=make_pp(), payments=[payment])
    assert rule.evaluate(ctx) == []
