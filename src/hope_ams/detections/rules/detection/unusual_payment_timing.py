from datetime import date

from ..base import BaseRule, Finding, RuleContext


class UnusualPaymentTimingRule(BaseRule):
    name = "unusual_payment_timing"
    phase = "detection"
    description = "Payment delivery date is significantly outside the normal distribution"
    default_severity = "low"
    default_config = {"max_days_from_mean": 30}

    @staticmethod
    def _parse_optional_date(dd: str | date | None) -> date | None:
        if not dd:
            return None
        try:
            if isinstance(dd, str):
                parsed = date.fromisoformat(dd.split("T")[0])
            else:
                parsed = dd
        except ValueError, TypeError:
            return None
        return parsed

    def evaluate(self, ctx: RuleContext) -> list[Finding]:
        delivery_dates = []
        for payment in ctx.payments:
            d = self._parse_optional_date(payment.get("delivery_date"))
            if d is not None:
                delivery_dates.append(d)

        if len(delivery_dates) < 5:
            return []

        ref_date = delivery_dates[len(delivery_dates) // 2]
        max_days = self.get_config(ctx).get("max_days_from_mean", 30)
        findings = []
        for payment in ctx.payments:
            dd = payment.get("delivery_date")
            d = self._parse_optional_date(dd)
            if d is None:
                continue
            offset = abs((d - ref_date).days)
            if offset > max_days:
                findings.append(
                    Finding(
                        severity=self.default_severity,
                        title=f"Unusual delivery date {dd} (offset: {offset} days from median)",
                        description=(
                            f"Payment {payment.get('unicef_id', '')} "
                            f"delivered on {dd}, which is {offset} days "
                            f"from the median delivery date {ref_date}"
                        ),
                        object_type="payment",
                        object_id=payment.get("id", ""),
                        object_unicef_id=payment.get("unicef_id", ""),
                        metadata={
                            "delivery_date": str(d),
                            "median_date": str(ref_date),
                            "offset_days": offset,
                            "max_offset": max_days,
                        },
                        household_id=payment.get("household_id"),
                    )
                )
        return findings
