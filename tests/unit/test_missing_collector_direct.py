from __future__ import annotations

import uuid


from hope_ams.detections.rules.base import RuleContext
from hope_ams.detections.rules.prevention.missing_collector import MissingCollectorRule

from tests.unit.conftest import pp_data


class TestMissingCollectorDirect:
    """Direct test of MissingCollectorRule logic."""

    def test_no_collector_fires(self) -> None:
        """When snapshot has no primary/alternate collector, the rule should fire."""
        ctx = RuleContext(
            phase="prevention",
            payment_plan=pp_data(),
            payments=[
                {
                    "snapshot_data": {},
                    "household_id": uuid.uuid4(),
                    "household_unicef_id": "HH-001",
                }
            ],
        )
        findings = MissingCollectorRule().evaluate(ctx)
        assert len(findings) == 1

    def test_has_primary_collector(self) -> None:
        """When snapshot has primary_collector set, the rule should NOT fire."""
        ctx = RuleContext(
            phase="prevention",
            payment_plan=pp_data(),
            payments=[
                {
                    "snapshot_data": {
                        "primary_collector": {"name": "John"},
                    },
                    "household_id": uuid.uuid4(),
                    "household_unicef_id": "HH-001",
                }
            ],
        )
        findings = MissingCollectorRule().evaluate(ctx)
        assert len(findings) == 0

    def test_has_alternate_collector(self) -> None:
        """When snapshot has alternate_collector set, the rule should NOT fire."""
        ctx = RuleContext(
            phase="prevention",
            payment_plan=pp_data(),
            payments=[
                {
                    "snapshot_data": {
                        "alternate_collector": {"name": "Jane"},
                    },
                    "household_id": uuid.uuid4(),
                    "household_unicef_id": "HH-001",
                }
            ],
        )
        findings = MissingCollectorRule().evaluate(ctx)
        assert len(findings) == 0

    def test_has_primary_role(self) -> None:
        """When snapshot has roles with PRIMARY, the rule should NOT fire."""
        ctx = RuleContext(
            phase="prevention",
            payment_plan=pp_data(),
            payments=[
                {
                    "snapshot_data": {
                        "roles": [{"role": "PRIMARY", "individual": "x"}],
                    },
                    "household_id": uuid.uuid4(),
                    "household_unicef_id": "HH-001",
                }
            ],
        )
        findings = MissingCollectorRule().evaluate(ctx)
        assert len(findings) == 0
