from datetime import UTC, date, datetime
from uuid import UUID

from django import forms

from ..base import BaseRule, Finding, RuleConfigForm, RuleContext


class PregnantChildConfig(RuleConfigForm):
    min_age = forms.IntegerField(label="Minimum age", initial=12)
    max_age = forms.IntegerField(label="Maximum age", initial=55)


class PregnantChildRule(BaseRule):
    name = "pregnant_child"
    verbose_name = "Pregnant Child"
    phase = "prevention"
    config_class = PregnantChildConfig
    description = "Individual is marked as pregnant but age is outside expected childbearing range"
    default_severity = "critical"
    default_config = {"min_age": 12, "max_age": 55}

    def evaluate(self, ctx: RuleContext) -> list[Finding]:
        findings = []
        today = datetime.now(tz=UTC).date()
        min_age = self.get_config(ctx).get("min_age", 12)
        max_age = self.get_config(ctx).get("max_age", 55)

        for payment in ctx.payments:
            individuals = payment.get("snapshot_data", {}).get("individuals", [])
            for ind in individuals:
                if not ind.get("pregnant"):
                    continue
                birth_date_str = ind.get("birth_date")
                if not birth_date_str:
                    continue
                try:
                    bd = date.fromisoformat(birth_date_str)
                except ValueError, TypeError:
                    continue
                age = today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))
                if age < min_age:
                    findings.append(
                        Finding(
                            severity=self.default_severity,
                            title=f"Pregnant individual aged {age} is below minimum age {min_age}",
                            description=(
                                f"Individual {ind.get('full_name', '')} "
                                f"(household {payment.get('household_unicef_id', '')}) "
                                f"is pregnant and aged {age}"
                            ),
                            object_type="individual",
                            object_id=UUID(str(ind.get("id", ""))),
                            object_unicef_id=ind.get("unicef_id", ""),
                            metadata={
                                "age": age,
                                "min_age": min_age,
                                "pregnant": True,
                                "full_name": ind.get("full_name"),
                            },
                            household_id=payment.get("household_id"),
                            individual_id=ind.get("id"),
                        )
                    )
                elif age > max_age:
                    findings.append(
                        Finding(
                            severity=self.default_severity,
                            title=f"Pregnant individual aged {age} exceeds maximum age {max_age}",
                            description=(
                                f"Individual {ind.get('full_name', '')} "
                                f"(household {payment.get('household_unicef_id', '')}) "
                                f"is pregnant and aged {age}"
                            ),
                            object_type="individual",
                            object_id=UUID(str(ind.get("id", ""))),
                            object_unicef_id=ind.get("unicef_id", ""),
                            metadata={
                                "age": age,
                                "max_age": max_age,
                                "pregnant": True,
                                "full_name": ind.get("full_name"),
                            },
                            household_id=payment.get("household_id"),
                            individual_id=ind.get("id"),
                        )
                    )
        return findings
