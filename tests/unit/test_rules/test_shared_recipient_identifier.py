import uuid

import pytest

from hope_ams.detection.rules.base import RuleContext
from hope_ams.detection.rules.shared_recipient_identifier import SharedRecipientIdentifierRule


@pytest.fixture
def rule():
    return SharedRecipientIdentifierRule()


def test_detects_shared_token_across_households(rule, make_pp, make_payment):
    p1 = make_payment(id=uuid.uuid4(), household_id=uuid.uuid4())
    p2 = make_payment(id=uuid.uuid4(), household_id=uuid.uuid4())
    ctx = RuleContext(phase="prevention", payment_plan=make_pp(), payments=[p1, p2])
    findings = rule.evaluate(ctx)
    assert len(findings) == 2
    assert findings[0].metadata["shared_household_count"] == 2


def test_no_finding_same_household(rule, make_pp, make_payment):
    hh = uuid.uuid4()
    p1 = make_payment(id=uuid.uuid4(), household_id=hh)
    p2 = make_payment(id=uuid.uuid4(), household_id=hh)
    ctx = RuleContext(phase="prevention", payment_plan=make_pp(), payments=[p1, p2])
    assert rule.evaluate(ctx) == []


def test_empty_token_skipped(rule, make_pp, make_payment):
    p1 = make_payment(household_id=uuid.uuid4(), token_number="")
    p2 = make_payment(household_id=uuid.uuid4(), token_number="")
    ctx = RuleContext(phase="prevention", payment_plan=make_pp(), payments=[p1, p2])
    assert rule.evaluate(ctx) == []


def test_none_household_id_skipped(rule, make_pp, make_payment):
    p1 = make_payment(household_id=None, token_number="TOKEN-1")
    p2 = make_payment(household_id=uuid.uuid4(), token_number="TOKEN-1")
    ctx = RuleContext(phase="prevention", payment_plan=make_pp(), payments=[p1, p2])
    assert rule.evaluate(ctx) == []


def test_different_fsp_not_grouped(rule, make_pp, make_payment):
    p1 = make_payment(household_id=uuid.uuid4(), financial_service_provider="FSP-A", token_number="TOKEN-1")
    p2 = make_payment(household_id=uuid.uuid4(), financial_service_provider="FSP-B", token_number="TOKEN-1")
    ctx = RuleContext(phase="prevention", payment_plan=make_pp(), payments=[p1, p2])
    assert rule.evaluate(ctx) == []


def test_three_households_same_token(rule, make_pp, make_payment):
    p1 = make_payment(id=uuid.uuid4(), household_id=uuid.uuid4())
    p2 = make_payment(id=uuid.uuid4(), household_id=uuid.uuid4())
    p3 = make_payment(id=uuid.uuid4(), household_id=uuid.uuid4())
    ctx = RuleContext(phase="prevention", payment_plan=make_pp(), payments=[p1, p2, p3])
    findings = rule.evaluate(ctx)
    assert len(findings) == 3
    assert findings[0].metadata["shared_household_count"] == 3
