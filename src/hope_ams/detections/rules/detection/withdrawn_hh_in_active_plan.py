from ..base import BaseRule, Finding, RuleContext


class WithdrawnHhInActivePlanRule(BaseRule):
    name = "withdrawn_hh_in_active_plan"
    phase = "detection"
    description = "A withdrawn household appears in an active (non-FINISHED/CLOSED) payment plan"
    default_severity = "critical"

    INACTIVE_STATUSES = ("FINISHED", "CLOSED")

    def evaluate(self, ctx: RuleContext) -> list[Finding]:
        findings = []
        pp_status = ctx.payment_plan.get("status", "")
        if pp_status in self.INACTIVE_STATUSES:
            return findings

        for payment in ctx.payments:
            snapshot = payment.get("snapshot_data", {})
            if snapshot.get("withdrawn"):
                findings.append(
                    Finding(
                        severity=self.default_severity,
                        title=f"Withdrawn household {payment.get('household_unicef_id', '')} in active plan",
                        description=(
                            f"Household {payment.get('household_unicef_id', '')} "
                            f"is marked as withdrawn but appears in payment plan "
                            f"{ctx.payment_plan.get('unicef_id', '')} (status: {pp_status})"
                        ),
                        object_type="household",
                        object_id=payment.get("household_id", ""),
                        object_unicef_id=payment.get("household_unicef_id", ""),
                        metadata={"withdrawn": True, "payment_plan_status": pp_status},
                        household_id=payment.get("household_id"),
                    )
                )
        return findings
