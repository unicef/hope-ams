from collections import defaultdict

from ..base import BaseRule, Finding, RuleContext


class UnrealisticSexRatioRule(BaseRule):
    name = "unrealistic_sex_ratio"
    phase = "detection"
    description = "An admin area within the payment plan has an extreme male/female ratio"
    default_severity = "medium"
    default_config = {"min_ratio": 0.5, "max_ratio": 1.5, "min_count": 10}

    def evaluate(self, ctx: RuleContext) -> list[Finding]:
        admin_sex: dict[str, dict[str, int]] = defaultdict(lambda: {"MALE": 0, "FEMALE": 0, "OTHER": 0})
        for payment in ctx.payments:
            snapshot = payment.get("snapshot_data", {})
            admin2 = snapshot.get("admin2_id", "unknown")
            individuals = snapshot.get("individuals", [])
            for ind in individuals:
                sex = ind.get("sex", "OTHER")
                if sex in admin_sex[admin2]:
                    admin_sex[admin2][sex] += 1
                else:
                    admin_sex[admin2][sex] = 1

        findings = []
        min_ratio = self.get_config(ctx).get("min_ratio", 0.5)
        max_ratio = self.get_config(ctx).get("max_ratio", 1.5)
        min_count = self.get_config(ctx).get("min_count", 10)
        for admin2, counts in admin_sex.items():
            total = counts["MALE"] + counts["FEMALE"]
            if total < min_count:
                continue
            ratio = counts["MALE"] / counts["FEMALE"] if counts["FEMALE"] > 0 else float("inf")
            if ratio < min_ratio or ratio > max_ratio:
                findings.append(
                    Finding(
                        severity=self.default_severity,
                        title=f"Unrealistic sex ratio {ratio:.2f} in admin area",
                        description=(
                            f"Admin area {admin2}: {counts['MALE']} males, "
                            f"{counts['FEMALE']} females (ratio: {ratio:.2f})"
                        ),
                        object_type="payment_plan",
                        object_id=ctx.payment_plan_id,
                        object_unicef_id=ctx.payment_plan.get("unicef_id", ""),
                        metadata={
                            "admin_area_id": admin2,
                            "males": counts["MALE"],
                            "females": counts["FEMALE"],
                            "ratio": round(ratio, 2),
                        },
                    )
                )
        return findings
