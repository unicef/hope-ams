import statistics

from ..base import BaseRule, Finding, RuleContext
import contextlib


class EntitlementOutlierRule(BaseRule):
    name = "entitlement_outlier"
    phase = "prevention"
    description = "Payment entitlement quantity deviates significantly from the mean (outside N standard deviations)"
    default_severity = "medium"
    default_config = {"std_dev_threshold": 3}

    def evaluate(self, ctx: RuleContext) -> list[Finding]:
        entitlements = []
        for payment in ctx.payments:
            eq = payment.get("entitlement_quantity")
            if eq is not None:
                with contextlib.suppress(ValueError, TypeError):
                    entitlements.append(float(eq))

        if len(entitlements) < 3:
            return []

        mean = statistics.mean(entitlements)
        stdev = statistics.stdev(entitlements) if len(entitlements) > 1 else 0
        if stdev == 0:
            return []

        threshold = self.get_config(ctx).get("std_dev_threshold", 3)
        findings = []
        for payment in ctx.payments:
            eq = payment.get("entitlement_quantity")
            if eq is None:
                continue
            try:
                val = float(eq)
            except ValueError, TypeError:
                continue
            if abs(val - mean) > threshold * stdev:
                findings.append(
                    Finding(
                        severity=self.default_severity,
                        title=f"Entitlement {eq} is {abs(val - mean) / stdev:.1f}std from mean",
                        description=(
                            f"Household {payment.get('household_unicef_id', '')} "
                            f"has entitlement {eq} (mean: {mean:.2f}, "
                            f"std: {stdev:.2f})"
                        ),
                        object_type="payment",
                        object_id=payment.get("id", ""),
                        object_unicef_id=payment.get("unicef_id", ""),
                        metadata={
                            "entitlement": val,
                            "mean": round(mean, 2),
                            "std_dev": round(stdev, 2),
                            "z_score": round(abs(val - mean) / stdev, 2),
                        },
                        household_id=payment.get("household_id"),
                    )
                )
        return findings
