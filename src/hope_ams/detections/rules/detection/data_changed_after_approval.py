from ..base import BaseRule, Finding, RuleContext


class DataChangedAfterApprovalRule(BaseRule):
    name = "data_changed_after_approval"
    phase = "detection"
    description = "Current household data differs from the frozen snapshot data (requires HOPE to provide current data)"
    default_severity = "critical"

    KEY_FIELDS = ["size", "address", "residence_status"]

    def evaluate(self, ctx: RuleContext) -> list[Finding]:
        findings = []
        for payment in ctx.payments:
            snapshot = payment.get("snapshot_data", {})
            current = payment.get("current_household_data")
            if not current:
                continue
            changes = {}
            for field in self.KEY_FIELDS:
                sv = snapshot.get(field)
                cv = current.get(field)
                if sv != cv:
                    changes[field] = {"snapshot": sv, "current": cv}
            if changes:
                findings.append(
                    Finding(
                        severity=self.default_severity,
                        title=f"Household data changed after snapshot for {payment.get('household_unicef_id', '')}",
                        description=f"Fields changed: {', '.join(changes.keys())}",
                        object_type="household",
                        object_id=payment.get("household_id", ""),
                        object_unicef_id=payment.get("household_unicef_id", ""),
                        metadata={"changes": changes},
                        household_id=payment.get("household_id"),
                    )
                )
        return findings
