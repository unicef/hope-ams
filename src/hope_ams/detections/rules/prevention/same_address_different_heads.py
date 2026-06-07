from collections import defaultdict

from ..base import BaseRule, Finding, RuleContext


class SameAddressDifferentHeadsRule(BaseRule):
    name = "same_address_different_heads"
    phase = "prevention"
    description = "Multiple households share the same address but have different heads"
    default_severity = "medium"

    def evaluate(self, ctx: RuleContext) -> list[Finding]:
        address_map: dict[str, list[dict]] = defaultdict(list)
        for payment in ctx.payments:
            snapshot = payment.get("snapshot_data", {})
            address = snapshot.get("address", "").strip()
            if not address:
                continue
            individuals = snapshot.get("individuals", [])
            head_name = ""
            for ind in individuals:
                if ind.get("relationship") == "HEAD":
                    head_name = ind.get("full_name", "")
                    break
            address_map[address].append(
                {
                    "household_id": payment.get("household_id", ""),
                    "household_unicef_id": payment.get("household_unicef_id", ""),
                    "head_name": head_name,
                }
            )

        findings = []
        for address, entries in address_map.items():
            if len(entries) > 1:
                heads = {e["head_name"] for e in entries if e["head_name"]}
                if len(heads) > 1:
                    hh_list = ", ".join(f"{e['household_unicef_id']} (head: {e['head_name']})" for e in entries)
                    findings.append(
                        Finding(
                            severity=self.default_severity,
                            title=f"Address '{address}' shared by {len(entries)} households with different heads",
                            description=f"Households at same address: {hh_list}",
                            object_type="household",
                            object_id="",
                            object_unicef_id="",
                            metadata={"address": address, "households": entries},
                        )
                    )
        return findings
