from ..base import BaseRule, Finding, RuleContext


class DistributedButNotDeliveredRule(BaseRule):
    name = "distributed_but_not_delivered"
    phase = "detection"
    description = "Payment has a SUCCESS status but delivered_quantity is zero or null"
    default_severity = "high"

    SUCCESS_STATUSES = ("Distribution Successful", "Transaction Successful", "Partially Distributed")

    def evaluate(self, ctx: RuleContext) -> list[Finding]:
        findings = []
        for payment in ctx.payments:
            status = payment.get("status")
            if status not in self.SUCCESS_STATUSES:
                continue
            dq = payment.get("delivered_quantity")
            if dq is None or float(dq) == 0:
                findings.append(
                    Finding(
                        severity=self.default_severity,
                        title=f"Payment {payment.get('unicef_id', '')} is '{status}' with zero delivered",
                        description=(
                            f"Payment {payment.get('unicef_id', '')} has "
                            f"status '{status}' but delivered_quantity is {dq}"
                        ),
                        object_type="payment",
                        object_id=payment.get("id", ""),
                        object_unicef_id=payment.get("unicef_id", ""),
                        metadata={"status": status, "delivered_quantity": dq},
                        household_id=payment.get("household_id"),
                    )
                )
        return findings
