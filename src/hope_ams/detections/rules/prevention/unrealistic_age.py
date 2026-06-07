from datetime import date, datetime

from ..base import BaseRule, Finding, RuleContext


class UnrealisticAgeRule(BaseRule):
    name = "unrealistic_age"
    phase = "prevention"
    description = "Individual has an unrealistic age (>110 or birth date in the future)"
    default_severity = "critical"
    default_config = {"max_age": 110}

    def evaluate(self, ctx: RuleContext) -> list[Finding]:
        findings = []
        today = datetime.now(datetime.UTC).date()
        max_age = self.get_config(ctx).get("max_age", 110)
        for payment in ctx.payments:
            individuals = payment.get("snapshot_data", {}).get("individuals", [])
            for ind in individuals:
                birth_date_str = ind.get("birth_date")
                if not birth_date_str:
                    continue
                try:
                    bd = date.fromisoformat(birth_date_str)
                except ValueError, TypeError:
                    continue
                if bd > today:
                    findings.append(
                        Finding(
                            severity=self.default_severity,
                            title=f"Birth date {birth_date_str} is in the future",
                            description=(
                                f"Individual {ind.get('full_name', '')} "
                                f"has birth date {birth_date_str} "
                                f"which is in the future"
                            ),
                            object_type="individual",
                            object_id=str(ind.get("id", "")),
                            object_unicef_id=ind.get("unicef_id", ""),
                            metadata={"birth_date": birth_date_str, "full_name": ind.get("full_name")},
                            household_id=payment.get("household_id"),
                            individual_id=ind.get("id"),
                        )
                    )
                    continue
                age = today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))
                if age > max_age:
                    findings.append(
                        Finding(
                            severity=self.default_severity,
                            title=f"Individual age {age} exceeds maximum {max_age}",
                            description=(
                                f"Individual {ind.get('full_name', '')} has age {age} (birth date: {birth_date_str})"
                            ),
                            object_type="individual",
                            object_id=str(ind.get("id", "")),
                            object_unicef_id=ind.get("unicef_id", ""),
                            metadata={
                                "age": age,
                                "birth_date": birth_date_str,
                                "max_age": max_age,
                                "full_name": ind.get("full_name"),
                            },
                            household_id=payment.get("household_id"),
                            individual_id=ind.get("id"),
                        )
                    )
        return findings
