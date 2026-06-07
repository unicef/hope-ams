from __future__ import annotations


from hope_ams.detections.rules.base import RuleContext
from hope_ams.detections.rules.detection.delivered_vs_received_mismatch import DeliveredVsReceivedMismatchRule
from hope_ams.detections.rules.detection.data_changed_after_approval import DataChangedAfterApprovalRule
from hope_ams.detections.rules.detection.withdrawn_hh_in_active_plan import WithdrawnHhInActivePlanRule
from hope_ams.detections.rules.detection.empty_household_active import EmptyHouseholdActiveRule
from hope_ams.detections.rules.detection.duplicate_payment_same_cycle import DuplicatePaymentSameCycleRule

from tests.unit.conftest import pp_data


def _ctx(payments: list[dict], phase: str = "detection", **cfg: dict) -> RuleContext:
    return RuleContext(
        phase=phase,
        payment_plan=pp_data(),
        payments=payments,
        config=cfg,
    )


class TestDeliveredVsReceivedMismatchRule:
    def test_no_issue(self, sample_payment: dict) -> None:
        p = {**sample_payment, "delivered_quantity": 500.0}
        p["verification"] = {"received_amount": 500.0, "status": "verified"}
        findings = DeliveredVsReceivedMismatchRule().evaluate(_ctx([p]))
        assert len(findings) == 0

    def test_mismatch(self, sample_payment: dict) -> None:
        p = {**sample_payment, "delivered_quantity": 500.0}
        p["verification"] = {"received_amount": 100.0, "status": "verified"}
        findings = DeliveredVsReceivedMismatchRule().evaluate(_ctx([p]))
        assert len(findings) == 1
        assert findings[0].severity == "high"


class TestDataChangedAfterApprovalRule:
    def test_no_current_data(self, sample_payment: dict) -> None:
        p = {**sample_payment}
        p.pop("current_household_data", None)
        findings = DataChangedAfterApprovalRule().evaluate(_ctx([p]))
        assert len(findings) == 0

    def test_no_changes(self, sample_payment: dict) -> None:
        p = {
            **sample_payment,
            "current_household_data": {"size": 4, "address": "123 Main St", "residence_status": "refugee"},
        }
        findings = DataChangedAfterApprovalRule().evaluate(_ctx([p]))
        assert len(findings) == 0

    def test_changes_detected(self, sample_payment: dict) -> None:
        p = {
            **sample_payment,
            "current_household_data": {"size": 6, "address": "456 Oak Ave", "residence_status": "refugee"},
        }
        findings = DataChangedAfterApprovalRule().evaluate(_ctx([p]))
        assert len(findings) == 1
        assert findings[0].severity == "critical"
        assert "size" in findings[0].metadata["changes"]
        assert "address" in findings[0].metadata["changes"]


class TestWithdrawnHhInActivePlanRule:
    def test_no_issue(self, sample_payment: dict) -> None:
        findings = WithdrawnHhInActivePlanRule().evaluate(_ctx([sample_payment]))
        assert len(findings) == 0

    def test_withdrawn(self, sample_payment: dict) -> None:
        p = {**sample_payment}
        p["snapshot_data"]["withdrawn"] = True
        findings = WithdrawnHhInActivePlanRule().evaluate(_ctx([p]))
        assert len(findings) == 1
        assert findings[0].severity == "critical"


class TestEmptyHouseholdActiveRule:
    def test_no_issue(self, sample_payment: dict) -> None:
        findings = EmptyHouseholdActiveRule().evaluate(_ctx([sample_payment]))
        assert len(findings) == 0

    def test_empty_household(self, sample_payment: dict) -> None:
        p = {**sample_payment}
        p["snapshot_data"]["size"] = 0
        findings = EmptyHouseholdActiveRule().evaluate(_ctx([p]))
        assert len(findings) == 1
        assert findings[0].severity == "high"


class TestDuplicatePaymentSameCycleRule:
    def test_no_duplicates(self, sample_payment: dict) -> None:
        p1 = {**sample_payment, "id": "pmt-1", "status": "Distribution Successful", "household_id": "hh-1"}
        p2 = {**sample_payment, "id": "pmt-2", "status": "Distribution Successful", "household_id": "hh-2"}
        findings = DuplicatePaymentSameCycleRule().evaluate(_ctx([p1, p2]))
        assert len(findings) == 0

    def test_duplicates(self, sample_payment: dict) -> None:
        p1 = {**sample_payment, "id": "pmt-1", "status": "Distribution Successful", "household_id": "hh-1"}
        p2 = {**sample_payment, "id": "pmt-2", "status": "Distribution Successful", "household_id": "hh-1"}
        findings = DuplicatePaymentSameCycleRule().evaluate(_ctx([p1, p2]))
        assert len(findings) >= 1
