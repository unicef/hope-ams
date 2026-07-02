from typing import Any
from uuid import UUID

from ..base import BaseRule, Finding, RuleContext


class DataChangedAfterApprovalRule(BaseRule):
    name = "data_changed_after_approval"
    verbose_name = "Data Changed After Approval"
    phase = "detection"
    description = "Household data has changed since payment plan approval"
    default_severity = "critical"

    def evaluate(self, ctx: RuleContext) -> list[Finding]:
        findings: list[Finding] = []
        for payment in ctx.payments:
            current = payment.get("current_household_data")
            if not current:
                continue
            snapshot = payment.get("snapshot_data", {})
            changes = {
                field: {"from": snapshot.get(field), "to": value}
                for field, value in current.items()
                if field in snapshot and snapshot.get(field) != value
            }
            extra_fields = {field: value for field, value in current.items() if field not in snapshot}
            if changes or extra_fields:
                metadata: dict[str, Any] = {}
                if changes:
                    metadata["changes"] = {k: v["to"] for k, v in changes.items()}
                    metadata["changed_fields"] = {k: {"from": v["from"], "to": v["to"]} for k, v in changes.items()}
                if extra_fields:
                    metadata["new_fields"] = extra_fields
                findings.append(
                    Finding(
                        severity=self.default_severity,
                        title="Household data changed after approval",
                        description=(
                            f"Payment {payment.get('unicef_id', '')} "
                            f"(household {payment.get('household_unicef_id', '')}) "
                            f"has data changes: {', '.join(changes)}"
                        ),
                        object_type="payment",
                        object_id=UUID(str(payment.get("id", ""))),
                        object_unicef_id=payment.get("unicef_id", ""),
                        metadata=metadata,
                        household_id=payment.get("household_id"),
                    )
                )
        return findings
