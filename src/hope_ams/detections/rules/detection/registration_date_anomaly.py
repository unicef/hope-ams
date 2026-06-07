from datetime import date

from ..base import BaseRule, Finding, RuleContext


class RegistrationDateAnomalyRule(BaseRule):
    name = "registration_date_anomaly"
    phase = "detection"
    description = "Program registration date is before the registration data import creation date"
    default_severity = "medium"

    def evaluate(self, ctx: RuleContext) -> list[Finding]:
        findings = []
        for payment in ctx.payments:
            snapshot = payment.get("snapshot_data", {})
            first_reg = snapshot.get("first_registration_date")
            last_reg = snapshot.get("last_registration_date")
            if not first_reg:
                continue
            try:
                reg_date = date.fromisoformat(first_reg.split("T")[0])
            except ValueError, TypeError:
                continue
            if last_reg:
                try:
                    rdi_date = date.fromisoformat(last_reg.split("T")[0])
                except ValueError, TypeError:
                    rdi_date = None
                if rdi_date and reg_date < rdi_date:
                    diff = (rdi_date - reg_date).days
                    findings.append(
                        Finding(
                            severity=self.default_severity,
                            title=f"Registration date {first_reg} before import date {last_reg}",
                            description=(
                                f"Household {payment.get('household_unicef_id', '')}: "
                                f"first registration {first_reg} is {diff} days "
                                f"before import {last_reg}"
                            ),
                            object_type="household",
                            object_id=payment.get("household_id", ""),
                            object_unicef_id=payment.get("household_unicef_id", ""),
                            metadata={
                                "first_registration_date": first_reg,
                                "last_registration_date": last_reg,
                                "diff_days": diff,
                            },
                            household_id=payment.get("household_id"),
                        )
                    )
        return findings
