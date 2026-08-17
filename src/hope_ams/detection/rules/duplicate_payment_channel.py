from uuid import UUID

from hope_ams.models.choices import Phase

from .base import BaseRule, Finding, RuleContext


class DuplicatePaymentChannelRule(BaseRule):
    name = "duplicate_payment_channel"
    verbose_name = "Duplicate Payment Channels"
    phases = [Phase.PREVENTION, Phase.DETECTION]
    default_severity = "critical"
    description = "Multiple payments share the same FSP, delivery type, and token number for the same household"
    default_config = {}

    def evaluate(self, ctx: RuleContext) -> list[Finding]:
        findings = []
        groups: dict[tuple, list[dict]] = {}

        for payment in ctx.payments:
            token = payment.get("token_number", "")
            if not token:
                continue
            key = (
                payment.get("financial_service_provider", ""),
                payment.get("delivery_type", ""),
                token,
            )
            groups.setdefault(key, []).append(payment)

        for key, payments in groups.items():
            if len(payments) <= 1:
                continue
            duplicate_ids = [str(p["id"]) for p in payments]
            fsp, delivery_type, token = key
            findings.extend(
                Finding(
                    severity=self.default_severity,
                    title=f"Duplicate payment channel: token {token}",
                    description=(
                        f"Payment {payment.get('unicef_id', payment.get('id', ''))} "
                        f"(household {payment.get('household_unicef_id', '')}) "
                        f"shares token '{token}' with {len(payments) - 1} other payment(s)"
                    ),
                    object_type="payment",
                    object_id=UUID(str(payment["id"])),
                    object_unicef_id=str(payment.get("unicef_id", "")),
                    metadata={
                        "token_number": token,
                        "fsp": fsp,
                        "delivery_type": delivery_type,
                        "duplicate_count": len(payments),
                        "duplicate_payment_ids": duplicate_ids,
                    },
                    payment_id=payment.get("id"),
                    household_id=payment.get("household_id"),
                )
                for payment in payments
            )
        return findings
