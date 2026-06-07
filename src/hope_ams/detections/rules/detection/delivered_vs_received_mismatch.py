from decimal import Decimal

from ..base import BaseRule, Finding, RuleContext


class DeliveredVsReceivedMismatchRule(BaseRule):
    name = "delivered_vs_received_mismatch"
    phase = "detection"
    description = "The delivered quantity differs from the received amount reported in payment verification"
    default_severity = "high"
    default_config = {"tolerance": 0.01}

    def evaluate(self, ctx: RuleContext) -> list[Finding]:
        findings = []
        tolerance = Decimal(str(self.get_config(ctx).get("tolerance", 0.01)))
        for payment in ctx.payments:
            verification = payment.get("verification")
            if not verification:
                continue
            delivered = payment.get("delivered_quantity")
            received = verification.get("received_amount")
            if delivered is None or received is None:
                continue
            try:
                d = Decimal(str(delivered))
                r = Decimal(str(received))
            except ValueError, TypeError:
                continue
            if abs(d - r) > tolerance:
                findings.append(
                    Finding(
                        severity=self.default_severity,
                        title=f"Delivered {d} ≠ received {r}",
                        description=(
                            f"Payment {payment.get('unicef_id', '')}: "
                            f"delivered {d} but beneficiary reported receiving {r}"
                        ),
                        object_type="payment",
                        object_id=payment.get("id", ""),
                        object_unicef_id=payment.get("unicef_id", ""),
                        metadata={"delivered_quantity": str(d), "received_amount": str(r), "diff": str(d - r)},
                        household_id=payment.get("household_id"),
                    )
                )
        return findings
