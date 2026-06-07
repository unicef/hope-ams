from collections import Counter

from ..base import BaseRule, Finding, RuleContext


class FspHighFailureRateRule(BaseRule):
    name = "fsp_high_failure_rate"
    phase = "detection"
    description = "A Financial Service Provider has a high proportion of failed/undelivered payments"
    default_severity = "high"
    default_config = {"failure_threshold_pct": 20}

    FAILED_STATUSES = ("Transaction Erroneous", "Force failed", "Manually Cancelled", "Not Distributed")

    def evaluate(self, ctx: RuleContext) -> list[Finding]:
        fsp_totals: dict[str, int] = Counter()
        fsp_failures: dict[str, int] = Counter()

        for payment in ctx.payments:
            fsp = payment.get("financial_service_provider", "Unknown")
            fsp_totals[fsp] += 1
            if payment.get("status") in self.FAILED_STATUSES:
                fsp_failures[fsp] += 1

        findings = []
        threshold = self.get_config(ctx).get("failure_threshold_pct", 20)
        for fsp, total in fsp_totals.items():
            failures = fsp_failures.get(fsp, 0)
            if total > 0 and (failures / total * 100) > threshold:
                pct = round(failures / total * 100, 1)
                findings.append(
                    Finding(
                        severity=self.default_severity,
                        title=f"FSP {fsp} has {pct}% failure rate",
                        description=(
                            f"FSP {fsp} has {failures}/{total} failed payments "
                            f"({pct}%) in plan {ctx.payment_plan.get('unicef_id', '')}"
                        ),
                        object_type="payment_plan",
                        object_id=ctx.payment_plan_id,
                        object_unicef_id=ctx.payment_plan.get("unicef_id", ""),
                        metadata={"fsp": fsp, "failed": failures, "total": total, "failure_pct": pct},
                    )
                )
        return findings
