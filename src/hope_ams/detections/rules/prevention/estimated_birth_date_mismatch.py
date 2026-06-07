from datetime import date, datetime

from ..base import BaseRule, Finding, RuleContext


class EstimatedBirthDateMismatchRule(BaseRule):
    name = "estimated_birth_date_mismatch"
    phase = "prevention"
    description = "Birth date is estimated and age_at_registration doesn't match the calculated age from birth date"
    default_severity = "medium"
    default_config = {"max_age_diff": 2}

    def evaluate(self, ctx: RuleContext) -> list[Finding]:
        findings = []
        today = datetime.now(datetime.UTC).date()
        max_diff = self.get_config(ctx).get("max_age_diff", 2)

        for payment in ctx.payments:
            individuals = payment.get("snapshot_data", {}).get("individuals", [])
            for ind in individuals:
                if not ind.get("estimated_birth_date"):
                    continue
                birth_date_str = ind.get("birth_date")
                age_at_reg = ind.get("age_at_registration")
                if not birth_date_str or age_at_reg is None:
                    continue
                try:
                    bd = date.fromisoformat(birth_date_str)
                    age_at_reg = float(age_at_reg)
                except ValueError, TypeError:
                    continue
                calculated_age = today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))
                diff = abs(calculated_age - age_at_reg)
                if diff > max_diff:
                    findings.append(
                        Finding(
                            severity=self.default_severity,
                            title=f"Estimated birth date mismatch for {ind.get('full_name', '')}",
                            description=(
                                f"Individual {ind.get('full_name', '')}: "
                                f"estimated birth date gives age {calculated_age}, "
                                f"but age_at_registration is {age_at_reg}"
                            ),
                            object_type="individual",
                            object_id=str(ind.get("id", "")),
                            object_unicef_id=ind.get("unicef_id", ""),
                            metadata={
                                "full_name": ind.get("full_name"),
                                "birth_date": birth_date_str,
                                "calculated_age": calculated_age,
                                "age_at_registration": age_at_reg,
                                "diff": diff,
                            },
                            household_id=payment.get("household_id"),
                            individual_id=ind.get("id"),
                        )
                    )
        return findings
