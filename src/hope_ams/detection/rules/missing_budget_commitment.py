from uuid import UUID

from hope_ams.models.choices import Phase

from .base import BaseRule, Finding, RuleContext


class MissingBudgetCommitmentRule(BaseRule):
    name = "missing_budget_commitment"
    verbose_name = "Payment Plan Without Budget Commitment"
    phases = [Phase.PREVENTION]
    default_severity = "medium"
    description = "The payment plan has no total entitled quantity, indicating a missing budget commitment"
    default_config = {}

    def evaluate(self, ctx: RuleContext) -> list[Finding]:
        if ctx.payment_plan.get("total_entitled_quantity") is not None:
            return []
        return [
            Finding(
                severity=self.default_severity,
                title="Payment plan missing budget commitment",
                description=(
                    f"Payment plan {ctx.payment_plan.get('unicef_id', ctx.payment_plan.get('id', ''))} "
                    f"has no total entitled quantity set"
                ),
                object_type="payment_plan",
                object_id=UUID(str(ctx.payment_plan["id"])),
                object_unicef_id=str(ctx.payment_plan.get("unicef_id", "")),
                metadata={
                    "programme_id": ctx.programme_id,
                    "office_id": ctx.office_id,
                },
            )
        ]
