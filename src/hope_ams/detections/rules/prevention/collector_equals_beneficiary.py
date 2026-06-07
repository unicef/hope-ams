from ..base import BaseRule, Finding, RuleContext


class CollectorEqualsBeneficiaryRule(BaseRule):
    name = "collector_equals_beneficiary"
    phase = "prevention"
    description = (
        "The payment collector is the same person as the head of household (potential conflict of interest flag)"
    )
    default_severity = "low"

    def evaluate(self, ctx: RuleContext) -> list[Finding]:
        findings = []
        for payment in ctx.payments:
            snapshot = payment.get("snapshot_data", {})
            primary = snapshot.get("primary_collector")
            individuals = snapshot.get("individuals", [])
            head_id = None
            for ind in individuals:
                if ind.get("relationship") == "HEAD":
                    head_id = str(ind.get("id"))
                    break
            if primary and head_id and str(primary.get("id")) == head_id:
                findings.append(
                    Finding(
                        severity=self.default_severity,
                        title="Collector is also the head of household",
                        description=(
                            f"Household {payment.get('household_unicef_id', '')} "
                            f"has the same person as collector and head of household"
                        ),
                        object_type="household",
                        object_id=payment.get("household_id", ""),
                        object_unicef_id=payment.get("household_unicef_id", ""),
                        metadata={"collector_id": head_id},
                        household_id=payment.get("household_id"),
                    )
                )
        return findings
