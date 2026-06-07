from collections import defaultdict

from ..base import BaseRule, Finding, RuleContext


class SameWalletMultipleHouseholdsRule(BaseRule):
    name = "same_wallet_multiple_households"
    phase = "prevention"
    description = "Same wallet address used across different households"
    default_severity = "critical"

    def evaluate(self, ctx: RuleContext) -> list[Finding]:
        wallet_map: dict[str, set[str]] = defaultdict(set)
        for payment in ctx.payments:
            hh_id = payment.get("household_unicef_id", "")
            individuals = payment.get("snapshot_data", {}).get("individuals", [])
            for ind in individuals:
                wallet = ind.get("wallet_address")
                if wallet:
                    wallet_map[wallet].add(hh_id)
                account_data = ind.get("account_data", {})
                for field in ("bank_account_number", "number", "wallet_address"):
                    val = account_data.get(field)
                    if val:
                        wallet_map[str(val)].add(hh_id)

        findings = []
        for wallet, hh_ids in wallet_map.items():
            if len(hh_ids) > 1:
                hh_list = ", ".join(sorted(hh_ids))
                findings.append(
                    Finding(
                        severity=self.default_severity,
                        title=f"Wallet {wallet} shared across {len(hh_ids)} households",
                        description=f"Wallet/account {wallet} is used in households: {hh_list}",
                        object_type="household",
                        object_id="",
                        object_unicef_id=hh_list,
                        metadata={"wallet": wallet, "households": list(hh_ids)},
                    )
                )
        return findings
