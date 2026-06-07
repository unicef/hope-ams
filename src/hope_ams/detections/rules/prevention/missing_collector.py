from ..base import BaseRule, Finding, RuleContext


class MissingCollectorRule(BaseRule):
    name = "missing_collector"
    phase = "prevention"
    description = "Household has no PRIMARY or ALTERNATE collector assigned"
    default_severity = "high"

    def evaluate(self, ctx: RuleContext) -> list[Finding]:
        findings = []
        for payment in ctx.payments:
            snapshot = payment.get("snapshot_data", {})
            roles = snapshot.get("roles", [])
            primary = snapshot.get("primary_collector")
            alternate = snapshot.get("alternate_collector")

            if not primary and not alternate:
                role_types = {r.get("role") for r in roles}
                if "PRIMARY" not in role_types and "ALTERNATE" not in role_types:
                    findings.append(
                        Finding(
                            severity=self.default_severity,
                            title="Missing collector",
                            description=(
                                f"Household {payment.get('household_unicef_id', '')} "
                                f"has no PRIMARY or ALTERNATE collector assigned"
                            ),
                            object_type="household",
                            object_id=payment.get("household_id", ""),
                            object_unicef_id=payment.get("household_unicef_id", ""),
                            metadata={"roles": roles},
                            household_id=payment.get("household_id"),
                        )
                    )
        return findings
