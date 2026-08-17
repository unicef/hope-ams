from uuid import UUID

from hope_ams.models.choices import Phase

from .base import BaseRule, Finding, RuleContext


class ConflictedPaymentDeliveredRule(BaseRule):
    name = "conflicted_payment_delivered"
    verbose_name = "Payment Issued to Conflicted Beneficiary"
    phases = [Phase.DETECTION]
    default_severity = "critical"
    description = "A payment marked as conflicted was delivered with a non-zero quantity"
    default_config = {}

    def evaluate(self, ctx: RuleContext) -> list[Finding]:
        findings = []
        for payment in ctx.payments:
            if not payment.get("conflicted"):
                continue
            delivered = payment.get("delivered_quantity")
            if delivered is None:
                continue
            try:
                if float(delivered) <= 0:
                    continue
            except ValueError, TypeError:
                continue

            findings.append(
                Finding(
                    severity=self.default_severity,
                    title="Conflicted beneficiary received payment",
                    description=(
                        f"Payment {payment.get('unicef_id', payment.get('id', ''))} "
                        f"(household {payment.get('household_unicef_id', '')}) "
                        f"was delivered to a conflicted beneficiary: {delivered} {payment.get('currency', '')}"
                    ),
                    object_type="payment",
                    object_id=UUID(str(payment["id"])),
                    object_unicef_id=str(payment.get("unicef_id", "")),
                    metadata={
                        "delivered_quantity": delivered,
                        "household_unicef_id": payment.get("household_unicef_id"),
                        "financial_service_provider": payment.get("financial_service_provider"),
                    },
                    payment_id=payment.get("id"),
                    household_id=payment.get("household_id"),
                )
            )
        return findings
