from uuid import UUID

from hope_ams.models.choices import Phase

from .base import BaseRule, Finding, RuleContext


class SharedRecipientIdentifierRule(BaseRule):
    name = "shared_recipient_identifier"
    verbose_name = "Shared Payment Recipient Identifier"
    phases = [Phase.PREVENTION]
    default_severity = "high"
    description = "The same payment token is used by multiple distinct households, indicating proxy collection risk"
    default_config = {}

    def evaluate(self, ctx: RuleContext) -> list[Finding]:
        findings = []
        groups: dict[tuple, dict[str, list[dict]]] = {}

        for payment in ctx.payments:
            token = payment.get("token_number", "")
            household_id = payment.get("household_id")
            if not token or household_id is None:
                continue
            key = (payment.get("financial_service_provider", ""), token)
            hh_map = groups.setdefault(key, {})
            hh_map.setdefault(str(household_id), []).append(payment)

        for (fsp, token), hh_map in groups.items():
            if len(hh_map) <= 1:
                continue
            shared_household_ids = list(hh_map.keys())
            for payments in hh_map.values():
                findings.extend(
                    Finding(
                        severity=self.default_severity,
                        title=f"Token '{token}' shared across {len(hh_map)} households",
                        description=(
                            f"Payment {payment.get('unicef_id', payment.get('id', ''))} "
                            f"(household {payment.get('household_unicef_id', '')}) "
                            f"uses token '{token}' which is shared by {len(hh_map)} distinct households"
                        ),
                        object_type="payment",
                        object_id=UUID(str(payment["id"])),
                        object_unicef_id=str(payment.get("unicef_id", "")),
                        metadata={
                            "token_number": token,
                            "fsp": fsp,
                            "shared_household_count": len(hh_map),
                            "shared_household_ids": shared_household_ids,
                        },
                        payment_id=payment.get("id"),
                        household_id=payment.get("household_id"),
                    )
                    for payment in payments
                )
        return findings
