from uuid import UUID

from ..base import BaseRule, Finding, RuleContext


class SanctionListCrossRefRule(BaseRule):
    name = "sanction_list_cross_ref"
    phase = "prevention"
    description = "Individual has a confirmed sanction list match"
    default_severity = "critical"

    def evaluate(self, ctx: RuleContext) -> list[Finding]:
        return [
            Finding(
                severity=self.default_severity,
                title=f"Individual {ind.get('full_name', '')} confirmed on sanction list",
                description=(
                    f"Individual {ind.get('full_name', '')} "
                    f"(household {payment.get('household_unicef_id', '')}) "
                    f"has a confirmed sanction list match"
                ),
                object_type="individual",
                object_id=UUID(str(ind.get("id", ""))),
                object_unicef_id=ind.get("unicef_id", ""),
                metadata={
                    "full_name": ind.get("full_name"),
                    "sanction_list_confirmed_match": True,
                    "sanction_list_possible_match": ind.get("sanction_list_possible_match"),
                },
                household_id=payment.get("household_id"),
                individual_id=ind.get("id"),
            )
            for payment in ctx.payments
            for ind in payment.get("snapshot_data", {}).get("individuals", [])
            if ind.get("sanction_list_confirmed_match")
        ]
