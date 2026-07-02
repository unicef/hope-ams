from hope_ams.detection.rules.base import RuleContext
from hope_ams.detection.rules.detection.data_changed_after_approval import (
    DataChangedAfterApprovalRule,
)
from tests.unit.conftest import pp_data


def _ctx(payments: list[dict], phase: str = "detection", **cfg: dict) -> RuleContext:
    return RuleContext(
        phase=phase,
        payment_plan=pp_data(),
        payments=payments,
        config=cfg,
    )


def test_no_current_data(sample_payment: dict) -> None:
    p = {**sample_payment}
    p.pop("current_household_data", None)
    findings = DataChangedAfterApprovalRule().evaluate(_ctx([p]))
    assert len(findings) == 0


def test_no_changes(sample_payment: dict) -> None:
    p = {
        **sample_payment,
        "current_household_data": {
            "size": 4,
            "address": "123 Main St",
            "residence_status": "refugee",
        },
    }
    findings = DataChangedAfterApprovalRule().evaluate(_ctx([p]))
    assert len(findings) == 0


def test_changes_detected(sample_payment: dict) -> None:
    p = {
        **sample_payment,
        "current_household_data": {
            "size": 6,
            "address": "456 Oak Ave",
            "residence_status": "refugee",
        },
    }
    findings = DataChangedAfterApprovalRule().evaluate(_ctx([p]))
    assert len(findings) == 1
    assert findings[0].severity == "critical"
    assert "size" in findings[0].metadata["changes"]
    assert "address" in findings[0].metadata["changes"]


if __name__ == "__main__":
    import pytest

    pytest.main([__file__, "-v"])
