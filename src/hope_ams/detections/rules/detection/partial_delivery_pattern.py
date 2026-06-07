from collections import defaultdict

from ..base import BaseRule, Finding, RuleContext


class PartialDeliveryPatternRule(BaseRule):
    name = "partial_delivery_pattern"
    phase = "detection"
    description = "Systematic partial deliveries to households in the same admin area"
    default_severity = "low"
    default_config = {"partial_threshold_pct": 50, "min_count": 3}

    def evaluate(self, ctx: RuleContext) -> list[Finding]:
        admin_partials: dict[str, dict] = defaultdict(lambda: {"total": 0, "partial": 0})
        for payment in ctx.payments:
            snapshot = payment.get("snapshot_data", {})
            admin2 = snapshot.get("admin2_id")
            if not admin2:
                admin2 = "unknown"
            eq = payment.get("entitlement_quantity")
            dq = payment.get("delivered_quantity")
            admin_partials[admin2]["total"] += 1
            if eq and dq and float(dq) > 0 and float(dq) < float(eq):
                admin_partials[admin2]["partial"] += 1

        findings = []
        threshold = self.get_config(ctx).get("partial_threshold_pct", 50)
        min_count = self.get_config(ctx).get("min_count", 3)
        for admin2, counts in admin_partials.items():
            if counts["total"] >= min_count:
                pct = counts["partial"] / counts["total"] * 100
                if pct > threshold:
                    findings.append(
                        Finding(
                            severity=self.default_severity,
                            title=f"Admin area {admin2} has {pct:.0f}% partial deliveries",
                            description=(
                                f"Admin area {admin2}: "
                                f"{counts['partial']}/{counts['total']} "
                                f"payments were partially delivered"
                            ),
                            object_type="payment_plan",
                            object_id=ctx.payment_plan_id,
                            object_unicef_id=ctx.payment_plan.get("unicef_id", ""),
                            metadata={
                                "admin_area_id": admin2,
                                "total": counts["total"],
                                "partial": counts["partial"],
                                "partial_pct": round(pct, 1),
                            },
                        )
                    )
        return findings
