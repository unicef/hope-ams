from datetime import date, datetime

from ..base import BaseRule, Finding, RuleContext


class ChildHeadOfHouseholdRule(BaseRule):
    name = "child_head_of_household"
    phase = "prevention"
    description = "Head of household is under 18 years old"
    default_severity = "high"
    default_config = {"max_age": 18}

    def evaluate(self, ctx: RuleContext) -> list[Finding]:
        findings = []
        today = datetime.now(datetime.UTC).date()
        for payment in ctx.payments:
            individuals = payment.get("snapshot_data", {}).get("individuals", [])
            for ind in individuals:
                if ind.get("relationship") != "HEAD":
                    continue
                birth_date_str = ind.get("birth_date")
                if not birth_date_str:
                    continue
                try:
                    bd = date.fromisoformat(birth_date_str)
                except ValueError, TypeError:
                    continue
                age = today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))
                max_age = self.get_config(ctx).get("max_age", 18)
                if age < max_age:
                    findings.append(
                        Finding(
                            severity=self.default_severity,
                            title=f"Head of household is {age} years old",
                            description=(
                                f"Household {payment.get('household_unicef_id', '')} has a head of household aged {age}"
                            ),
                            object_type="household",
                            object_id=payment.get("household_id", ""),
                            object_unicef_id=payment.get("household_unicef_id", ""),
                            metadata={
                                "age": age,
                                "individual_id": str(ind.get("id", "")),
                                "relationship": ind.get("relationship"),
                            },
                            household_id=payment.get("household_id"),
                        )
                    )
        return findings
