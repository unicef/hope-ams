from __future__ import annotations

from datetime import datetime, timedelta

from hope_ams.detections.rules.base import RuleContext
from hope_ams.detections.rules.prevention.unrealistic_age import UnrealisticAgeRule
from hope_ams.detections.rules.prevention.pregnant_child import PregnantChildRule
from hope_ams.detections.rules.prevention.child_head_of_household import ChildHeadOfHouseholdRule
from hope_ams.detections.rules.prevention.missing_collector import MissingCollectorRule
from hope_ams.detections.rules.prevention.zero_entitlement_not_excluded import ZeroEntitlementNotExcludedRule
from hope_ams.detections.rules.prevention.excessive_household_size import ExcessiveHouseholdSizeRule

from tests.unit.conftest import pp_data


def _ctx(payments: list[dict], **cfg: dict) -> RuleContext:
    return RuleContext(
        phase="prevention",
        payment_plan=pp_data(),
        payments=payments,
        config=cfg,
    )


class TestUnrealisticAgeRule:
    def test_no_issue(self, sample_payment: dict) -> None:
        findings = UnrealisticAgeRule().evaluate(_ctx([sample_payment]))
        assert len(findings) == 0

    def test_future_birth_date(self, sample_payment: dict) -> None:
        future = (datetime.now(datetime.UTC).date() + timedelta(days=365)).isoformat()
        ind = sample_payment["snapshot_data"]["individuals"][0]
        ind["birth_date"] = future
        findings = UnrealisticAgeRule().evaluate(_ctx([sample_payment]))
        assert len(findings) == 1
        assert findings[0].severity == "critical"

    def test_age_over_max(self, sample_payment: dict) -> None:
        ind = sample_payment["snapshot_data"]["individuals"][0]
        ind["birth_date"] = "1800-01-01"
        findings = UnrealisticAgeRule().evaluate(_ctx([sample_payment]))
        assert len(findings) == 1
        assert "exceeds maximum" in findings[0].title

    def test_configurable_max_age(self, sample_payment: dict) -> None:
        config = {"rules": {"unrealistic_age": {"config": {"max_age": 30}}}}
        ind = sample_payment["snapshot_data"]["individuals"][0]
        ind["birth_date"] = "1985-06-10"
        findings = UnrealisticAgeRule().evaluate(_ctx([sample_payment], **config))
        assert len(findings) >= 1


class TestPregnantChildRule:
    def test_no_issue(self, sample_payment: dict) -> None:
        findings = PregnantChildRule().evaluate(_ctx([sample_payment]))
        assert len(findings) == 0

    def test_pregnant_child(self, sample_payment: dict) -> None:
        ind = sample_payment["snapshot_data"]["individuals"][1]
        ind["pregnant"] = True
        ind["birth_date"] = "2020-01-01"
        findings = PregnantChildRule().evaluate(_ctx([sample_payment]))
        assert len(findings) == 1
        assert findings[0].severity == "critical"


class TestChildHeadOfHouseholdRule:
    def test_no_issue(self, sample_payment: dict) -> None:
        findings = ChildHeadOfHouseholdRule().evaluate(_ctx([sample_payment]))
        assert len(findings) == 0

    def test_child_head(self, sample_payment: dict) -> None:
        ind = sample_payment["snapshot_data"]["individuals"][0]
        ind["birth_date"] = "2010-01-01"
        ind["relationship"] = "HEAD"
        findings = ChildHeadOfHouseholdRule().evaluate(_ctx([sample_payment]))
        assert len(findings) == 1
        assert findings[0].severity == "high"


class TestMissingCollectorRule:
    def test_no_issue(self, sample_payment: dict) -> None:
        findings = MissingCollectorRule().evaluate(_ctx([sample_payment]))
        assert len(findings) == 0

    def test_no_collector(self, sample_payment: dict) -> None:
        p = dict(sample_payment)
        p["snapshot_data"] = dict(sample_payment["snapshot_data"])
        del p["snapshot_data"]["primary_collector"]
        findings = MissingCollectorRule().evaluate(_ctx([p]))
        assert len(findings) >= 1


class TestZeroEntitlementNotExcludedRule:
    def test_no_issue(self, sample_payment: dict) -> None:
        findings = ZeroEntitlementNotExcludedRule().evaluate(_ctx([sample_payment]))
        assert len(findings) == 0

    def test_zero_entitlement_not_excluded(self, sample_payment: dict) -> None:
        sample_payment["entitlement_quantity"] = 0
        sample_payment["excluded"] = False
        findings = ZeroEntitlementNotExcludedRule().evaluate(_ctx([sample_payment]))
        assert len(findings) == 1
        assert findings[0].severity == "high"


class TestExcessiveHouseholdSizeRule:
    def test_no_issue(self, sample_payment: dict) -> None:
        findings = ExcessiveHouseholdSizeRule().evaluate(_ctx([sample_payment]))
        assert len(findings) == 0

    def test_excessive_size(self, sample_payment: dict) -> None:
        sample_payment["snapshot_data"]["size"] = 50
        findings = ExcessiveHouseholdSizeRule().evaluate(_ctx([sample_payment]))
        assert len(findings) == 1
        assert findings[0].severity == "medium"
