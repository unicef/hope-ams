from datetime import date, datetime

from ..base import BaseRule, Finding, RuleContext


class PendingPaymentStaleRule(BaseRule):
    name = "pending_payment_stale"
    phase = "detection"
    description = "Payment has been in a pending status for longer than the configured threshold"
    default_severity = "medium"
    default_config = {"max_pending_days": 30}

    PENDING_STATUSES = ("Pending", "Sent to Payment Gateway", "Sent to FSP")

    def evaluate(self, ctx: RuleContext) -> list[Finding]:
        findings = []
        max_days = self.get_config(ctx).get("max_pending_days", 30)
        today = datetime.now(datetime.UTC).date()

        for payment in ctx.payments:
            if payment.get("status") not in self.PENDING_STATUSES:
                continue
            delivery_date = payment.get("delivery_date")
            if not delivery_date:
                delivery_date = payment.get("entitlement_date")
            if not delivery_date:
                continue
            try:
                if isinstance(delivery_date, str):
                    d = date.fromisoformat(delivery_date.split("T")[0])
                else:
                    d = delivery_date
            except ValueError, TypeError:
                continue
            days_pending = (today - d).days
            if days_pending > max_days:
                findings.append(
                    Finding(
                        severity=self.default_severity,
                        title=f"Payment pending for {days_pending} days",
                        description=(
                            f"Payment {payment.get('unicef_id', '')} has been "
                            f"in status '{payment.get('status')}' for "
                            f"{days_pending} days (max: {max_days})"
                        ),
                        object_type="payment",
                        object_id=payment.get("id", ""),
                        object_unicef_id=payment.get("unicef_id", ""),
                        metadata={
                            "status": payment.get("status"),
                            "days_pending": days_pending,
                            "max_days": max_days,
                            "since_date": str(d),
                        },
                        household_id=payment.get("household_id"),
                    )
                )
        return findings
