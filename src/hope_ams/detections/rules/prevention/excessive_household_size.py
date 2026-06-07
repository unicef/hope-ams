from ..base import BaseRule, Finding, RuleContext


class ExcessiveHouseholdSizeRule(BaseRule):
    name = "excessive_household_size"
    phase = "prevention"
    description = "Household size exceeds configured maximum"
    default_severity = "medium"
    default_config = {"max_size": 15}

    def evaluate(self, ctx: RuleContext) -> list[Finding]:
        findings = []
        max_size = self.get_config(ctx).get("max_size", 15)
        for payment in ctx.payments:
            snapshot = payment.get("snapshot_data", {})
            size = snapshot.get("size", 0)
            if size > max_size:
                findings.append(
                    Finding(
                        severity=self.default_severity,
                        title=f"Household size {size} exceeds maximum {max_size}",
                        description=(
                            f"Household {payment.get('household_unicef_id', '')} has {size} members (max: {max_size})"
                        ),
                        object_type="household",
                        object_id=payment.get("household_id", ""),
                        object_unicef_id=payment.get("household_unicef_id", ""),
                        metadata={"size": size, "max_size": max_size},
                        household_id=payment.get("household_id"),
                    )
                )
        return findings
