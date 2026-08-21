import uuid

import pytest

from hope_ams.detection.rules.base import RuleContext
from hope_ams.detection.rules.duplicate_payment_channel import DuplicatePaymentChannelRule


@pytest.fixture
def rule():
    return DuplicatePaymentChannelRule()


def test_detects_duplicate_token(rule, make_pp, make_payment):
    p1 = make_payment(id=uuid.uuid4(), unicef_id="PMT-001")
    p2 = make_payment(id=uuid.uuid4(), unicef_id="PMT-002")
    ctx = RuleContext(phase="prevention", payment_plan=make_pp(), payments=[p1, p2])
    findings = rule.evaluate(ctx)
    assert len(findings) == 2
    for f in findings:
        assert f.metadata["duplicate_count"] == 2
        assert len(f.metadata["duplicate_payment_ids"]) == 2


def test_no_finding_for_unique_tokens(rule, make_pp, make_payment):
    p1 = make_payment(token_number="TOKEN-1")
    p2 = make_payment(token_number="TOKEN-2")
    ctx = RuleContext(phase="prevention", payment_plan=make_pp(), payments=[p1, p2])
    assert rule.evaluate(ctx) == []


def test_empty_token_skipped(rule, make_pp, make_payment):
    p1 = make_payment(token_number="")
    p2 = make_payment(token_number="")
    ctx = RuleContext(phase="prevention", payment_plan=make_pp(), payments=[p1, p2])
    assert rule.evaluate(ctx) == []


def test_different_fsp_not_grouped(rule, make_pp, make_payment):
    p1 = make_payment(financial_service_provider="FSP-A", token_number="TOKEN-1")
    p2 = make_payment(financial_service_provider="FSP-B", token_number="TOKEN-1")
    ctx = RuleContext(phase="prevention", payment_plan=make_pp(), payments=[p1, p2])
    assert rule.evaluate(ctx) == []


def test_three_way_duplicate(rule, make_pp, make_payment):
    p1 = make_payment(id=uuid.uuid4())
    p2 = make_payment(id=uuid.uuid4())
    p3 = make_payment(id=uuid.uuid4())
    ctx = RuleContext(phase="prevention", payment_plan=make_pp(), payments=[p1, p2, p3])
    findings = rule.evaluate(ctx)
    assert len(findings) == 3
    assert findings[0].metadata["duplicate_count"] == 3
