from ..base import BaseRule, Finding, RuleContext


class ZeroEntitlementNotExcludedRule(BaseRule):
    name = "zero_entitlement_not_excluded"
    phase = "prevention"
    description = "Payment has zero entitlement but household is not marked as excluded"
    default_severity = "high"

    def evaluate(self, ctx: RuleContext) -> list[Finding]:
        findings = []
        for payment in ctx.payments:
            eq = payment.get("entitlement_quantity")
            excluded = payment.get("excluded", False)
            if eq is not None and float(eq) == 0 and not excluded:
                findings.append(
                    Finding(
                        severity=self.default_severity,
                        title="Zero entitlement but household not excluded",
                        description=(
                            f"Household {payment.get('household_unicef_id', '')} has entitlement 0 but excluded=false"
                        ),
                        object_type="payment",
                        object_id=payment.get("id", ""),
                        object_unicef_id=payment.get("unicef_id", ""),
                        metadata={"entitlement_quantity": eq, "excluded": excluded},
                        household_id=payment.get("household_id"),
                    )
                )
        return findings
