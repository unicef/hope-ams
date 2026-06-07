from ..base import BaseRule, Finding, RuleContext


class PwdPrevalenceOutlierRule(BaseRule):
    name = "pwd_prevalence_outlier"
    phase = "detection"
    description = "Prevalence of Persons with Disabilities (PwD) differs significantly from the expected rate"
    default_severity = "low"
    default_config = {"expected_pwd_pct": 15, "deviation_pct": 50}

    def evaluate(self, ctx: RuleContext) -> list[Finding]:
        total = 0
        disabled = 0
        for payment in ctx.payments:
            individuals = payment.get("snapshot_data", {}).get("individuals", [])
            for ind in individuals:
                total += 1
                if ind.get("disability") == "DISABLED":
                    disabled += 1

        if total == 0:
            return []

        actual_pct = disabled / total * 100
        expected = self.get_config(ctx).get("expected_pwd_pct", 15)
        deviation = self.get_config(ctx).get("deviation_pct", 50)
        if actual_pct < expected * (1 - deviation / 100) or actual_pct > expected * (1 + deviation / 100):
            return [
                Finding(
                    severity=self.default_severity,
                    title=f"PwD prevalence {actual_pct:.1f}% deviates from expected {expected}%",
                    description=(
                        f"Payment plan has {disabled}/{total} individuals "
                        f"with disabilities ({actual_pct:.1f}%). "
                        f"Expected: ~{expected}%."
                    ),
                    object_type="payment_plan",
                    object_id=ctx.payment_plan_id,
                    object_unicef_id=ctx.payment_plan.get("unicef_id", ""),
                    metadata={
                        "total_individuals": total,
                        "disabled_count": disabled,
                        "actual_pct": round(actual_pct, 1),
                        "expected_pct": expected,
                    },
                )
            ]
        return []
