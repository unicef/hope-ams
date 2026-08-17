from datetime import UTC, datetime, timedelta
from uuid import UUID

from hope_ams.models.choices import Phase

from .base import BaseRule, Finding, RuleContext


class UnreconciledPaymentRule(BaseRule):
    name = "unreconciled_payment"
    verbose_name = "Unreconciled Payments After Window"
    phases = [Phase.DETECTION]
    default_severity = "high"
    description = "Payment has not been reconciled within the expected window after delivery"
    default_config = {"reconciliation_days": 30}

    def evaluate(self, ctx: RuleContext) -> list[Finding]:
        findings = []
        cfg = self.get_config(ctx)
        window = ctx.payment_plan.get("reconciliation_window_in_days") or cfg.get("reconciliation_days", 30)
        cutoff = datetime.now(tz=UTC) - timedelta(days=int(window))

        for payment in ctx.payments:
            if payment.get("delivered_quantity") is not None:
                continue
            if payment.get("excluded"):
                continue

            date_str = payment.get("delivery_date") or payment.get("entitlement_date")
            if not date_str:
                continue

            try:
                delivery_dt = datetime.fromisoformat(str(date_str))
                if delivery_dt.tzinfo is None:
                    delivery_dt = delivery_dt.replace(tzinfo=UTC)
            except ValueError, TypeError:
                continue

            if delivery_dt >= cutoff:
                continue

            days_outstanding = (datetime.now(tz=UTC) - delivery_dt).days
            findings.append(
                Finding(
                    severity=self.default_severity,
                    title=f"Payment unreconciled for {days_outstanding} days",
                    description=(
                        f"Payment {payment.get('unicef_id', payment.get('id', ''))} "
                        f"(household {payment.get('household_unicef_id', '')}) "
                        f"has not been reconciled after {days_outstanding} days"
                    ),
                    object_type="payment",
                    object_id=UUID(str(payment["id"])),
                    object_unicef_id=str(payment.get("unicef_id", "")),
                    metadata={
                        "fsp": payment.get("financial_service_provider"),
                        "days_outstanding": days_outstanding,
                        "reconciliation_window": window,
                        "delivery_date": date_str,
                    },
                    payment_id=payment.get("id"),
                    household_id=payment.get("household_id"),
                )
            )
        return findings
