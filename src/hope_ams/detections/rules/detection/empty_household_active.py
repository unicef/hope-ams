from ..base import BaseRule, Finding, RuleContext


class EmptyHouseholdActiveRule(BaseRule):
    name = "empty_household_active"
    phase = "detection"
    description = "Household has zero members but appears in an active payment plan"
    default_severity = "high"

    def evaluate(self, ctx: RuleContext) -> list[Finding]:
        findings = []
        for payment in ctx.payments:
            snapshot = payment.get("snapshot_data", {})
            size = snapshot.get("size", 0)
            if size == 0:
                findings.append(
                    Finding(
                        severity=self.default_severity,
                        title=f"Empty household {payment.get('household_unicef_id', '')} in payment plan",
                        description=(
                            f"Household {payment.get('household_unicef_id', '')} "
                            f"has size 0 but appears in payment plan "
                            f"{ctx.payment_plan.get('unicef_id', '')}"
                        ),
                        object_type="household",
                        object_id=payment.get("household_id", ""),
                        object_unicef_id=payment.get("household_unicef_id", ""),
                        metadata={"size": 0},
                        household_id=payment.get("household_id"),
                    )
                )
        return findings
