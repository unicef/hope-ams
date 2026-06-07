from collections import defaultdict

from ..base import BaseRule, Finding, RuleContext


class PhoneNumberReuseRule(BaseRule):
    name = "phone_number_reuse"
    phase = "prevention"
    description = "Same phone number used across different households in the same payment plan"
    default_severity = "high"

    def evaluate(self, ctx: RuleContext) -> list[Finding]:
        phone_map: dict[str, set[str]] = defaultdict(set)
        phone_individuals: dict[str, list[dict]] = defaultdict(list)

        for payment in ctx.payments:
            hh_id = payment.get("household_unicef_id", "")
            individuals = payment.get("snapshot_data", {}).get("individuals", [])
            for ind in individuals:
                for phone_key in ("phone_no", "phone_no_alternative", "payment_delivery_phone_no"):
                    phone = ind.get(phone_key)
                    if phone:
                        phone_map[phone].add(hh_id)
                        phone_individuals[phone].append(
                            {
                                "household": hh_id,
                                "individual": ind.get("full_name", ""),
                                "individual_id": str(ind.get("id", "")),
                            }
                        )

        findings = []
        for phone, hh_ids in phone_map.items():
            if len(hh_ids) > 1:
                hh_list = ", ".join(sorted(hh_ids))
                findings.append(
                    Finding(
                        severity=self.default_severity,
                        title=f"Phone {phone} shared across {len(hh_ids)} households",
                        description=f"Phone {phone} is used in households: {hh_list}",
                        object_type="household",
                        object_id="",
                        object_unicef_id=hh_list,
                        metadata={
                            "phone": phone,
                            "households": list(hh_ids),
                            "individuals": phone_individuals[phone],
                        },
                    )
                )
        return findings
