from datetime import UTC, date, datetime

from ..base import BaseRule, Finding, RuleContext


class ReconciliationOverdueRule(BaseRule):
    name = "reconciliation_overdue"
    phase = "detection"
    description = "Payment plan is in ACCEPTED status past its reconciliation window"
    default_severity = "high"
    default_config = {"default_reconciliation_window_days": 30}

    def evaluate(self, ctx: RuleContext) -> list[Finding]:
        findings: list[Finding] = []
        pp = ctx.payment_plan
        if pp.get("status") != "ACCEPTED":
            return findings

        window = pp.get("reconciliation_window_in_days")
        if window is None:
            window = self.get_config(ctx).get("default_reconciliation_window_days", 30)

        dispersion_start = pp.get("dispersion_start_date")
        if not dispersion_start:
            return findings

        try:
            if isinstance(dispersion_start, str):
                start_date = date.fromisoformat(dispersion_start)
            else:
                start_date = dispersion_start
        except ValueError, TypeError:
            return findings

        today = datetime.now(tz=UTC).date()
        due_date = start_date
        from datetime import timedelta

        due_date = start_date + timedelta(days=int(window))

        if today > due_date:
            overdue_days = (today - due_date).days
            unpaid = sum(
                1 for p in ctx.payments if p.get("status") in ("Pending", "Sent to Payment Gateway", "Sent to FSP")
            )
            findings.append(
                Finding(
                    severity=self.default_severity,
                    title=f"Reconciliation overdue by {overdue_days} days",
                    description=(
                        f"Payment plan {pp.get('unicef_id', '')} was due for "
                        f"reconciliation on {due_date} ({overdue_days} days ago). "
                        f"{unpaid} payments still pending."
                    ),
                    object_type="payment_plan",
                    object_id=pp.get("id", ""),
                    object_unicef_id=pp.get("unicef_id", ""),
                    metadata={
                        "dispersion_start": str(start_date),
                        "reconciliation_window": window,
                        "due_date": str(due_date),
                        "overdue_days": overdue_days,
                        "pending_payments": unpaid,
                    },
                )
            )
        return findings
