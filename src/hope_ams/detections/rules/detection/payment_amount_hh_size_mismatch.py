import contextlib

from ..base import BaseRule, Finding, RuleContext


class PaymentAmountHhSizeMismatchRule(BaseRule):
    name = "payment_amount_hh_size_mismatch"
    phase = "detection"
    description = "Per-capita payment amount deviates significantly from expected"
    default_severity = "medium"
    default_config = {"expected_per_capita": None, "deviation_threshold_pct": 50}

    def evaluate(self, ctx: RuleContext) -> list[Finding]:
        payments_with_size = []
        for payment in ctx.payments:
            snapshot = payment.get("snapshot_data", {})
            size = snapshot.get("size", 0)
            entitlement = payment.get("entitlement_quantity")
            if size > 0 and entitlement is not None:
                with contextlib.suppress(ValueError, TypeError):
                    payments_with_size.append(
                        {
                            "payment": payment,
                            "size": int(size),
                            "entitlement": float(entitlement),
                            "per_capita": float(entitlement) / int(size),
                        }
                    )

        if not payments_with_size:
            return []

        config = self.get_config(ctx)
        expected = config.get("expected_per_capita")
        if expected is None:
            expected = sum(p["per_capita"] for p in payments_with_size) / len(payments_with_size)

        threshold = config.get("deviation_threshold_pct", 50)
        findings = []
        for item in payments_with_size:
            p = item["payment"]
            deviation = abs(item["per_capita"] - expected) / expected * 100 if expected > 0 else 0
            if deviation > threshold:
                findings.append(
                    Finding(
                        severity=self.default_severity,
                        title=(
                            f"Per-capita amount {item['per_capita']:.2f} deviates "
                            f"{deviation:.0f}% from expected {expected:.2f}"
                        ),
                        description=(
                            f"Household {p.get('household_unicef_id', '')}: "
                            f"size {item['size']}, entitlement {item['entitlement']}, "
                            f"per-capita {item['per_capita']:.2f}"
                        ),
                        object_type="payment",
                        object_id=p.get("id", ""),
                        object_unicef_id=p.get("unicef_id", ""),
                        metadata={
                            "household_size": item["size"],
                            "entitlement": item["entitlement"],
                            "per_capita": round(item["per_capita"], 2),
                            "expected_per_capita": round(expected, 2),
                            "deviation_pct": round(deviation, 1),
                        },
                        household_id=p.get("household_id"),
                    )
                )
        return findings
