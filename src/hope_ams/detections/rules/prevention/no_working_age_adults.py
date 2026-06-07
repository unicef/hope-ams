from datetime import date, datetime

from ..base import BaseRule, Finding, RuleContext


class NoWorkingAgeAdultsRule(BaseRule):
    name = "no_working_age_adults"
    phase = "prevention"
    description = "Household has no working-age adults (18-59) with more than 3 children"
    default_severity = "high"
    default_config = {"min_working_age": 18, "max_working_age": 59, "max_children": 3}

    def evaluate(self, ctx: RuleContext) -> list[Finding]:
        findings = []
        today = datetime.now(datetime.UTC).date()
        min_age = self.get_config(ctx).get("min_working_age", 18)
        max_age = self.get_config(ctx).get("max_working_age", 59)
        max_children = self.get_config(ctx).get("max_children", 3)

        for payment in ctx.payments:
            individuals = payment.get("snapshot_data", {}).get("individuals", [])
            children = 0
            working_adults = 0
            for ind in individuals:
                birth_date_str = ind.get("birth_date")
                if not birth_date_str:
                    continue
                try:
                    bd = date.fromisoformat(birth_date_str)
                except ValueError, TypeError:
                    continue
                age = today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))
                if min_age <= age <= max_age:
                    working_adults += 1
                elif age < min_age:
                    children += 1

            if working_adults == 0 and children > max_children:
                findings.append(
                    Finding(
                        severity=self.default_severity,
                        title="No working-age adults with excessive dependents",
                        description=(
                            f"Household {payment.get('household_unicef_id', '')} "
                            f"has {children} children and 0 working-age adults (18-59)"
                        ),
                        object_type="household",
                        object_id=payment.get("household_id", ""),
                        object_unicef_id=payment.get("household_unicef_id", ""),
                        metadata={"children": children, "working_adults": working_adults},
                        household_id=payment.get("household_id"),
                    )
                )
        return findings
