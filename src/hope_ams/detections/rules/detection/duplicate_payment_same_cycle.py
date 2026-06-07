from uuid import UUID

from ..base import BaseRule, Finding, RuleContext


class DuplicatePaymentSameCycleRule(BaseRule):
    name = "duplicate_payment_same_cycle"
    phase = "detection"
    description = "Same household has multiple successful payments in the same payment plan cycle"
    default_severity = "critical"

    def evaluate(self, ctx: RuleContext) -> list[Finding]:
        hh_payments: dict[str, list[dict]] = {}
        for payment in ctx.payments:
            hh_id = payment.get("household_id")
            if not hh_id:
                continue
            if hh_id not in hh_payments:
                hh_payments[hh_id] = []
            hh_payments[hh_id].append(payment)

        findings = []
        success_statuses = ("Distribution Successful", "Transaction Successful")
        for hh_id, payments in hh_payments.items():
            successful = [p for p in payments if p.get("status") in success_statuses]
            if len(successful) > 1:
                unicef_ids = [p.get("unicef_id", "") for p in successful]
                findings.append(
                    Finding(
                        severity=self.default_severity,
                        title=f"Household has {len(successful)} successful payments",
                        description=(
                            f"Household {successful[0].get('household_unicef_id', '')} "
                            f"has {len(successful)} successful payments: "
                            f"{', '.join(unicef_ids)}"
                        ),
                        object_type="household",
                        object_id=UUID(str(hh_id)),
                        object_unicef_id=successful[0].get("household_unicef_id", ""),
                        metadata={"household_id": hh_id, "payment_ids": unicef_ids, "count": len(successful)},
                        household_id=UUID(str(hh_id)),
                    )
                )
        return findings
