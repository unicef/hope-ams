from collections import defaultdict

from ..base import BaseRule, Finding, RuleContext


class DocumentCrossProgramRule(BaseRule):
    name = "document_cross_program"
    phase = "prevention"
    description = "Same identity document number used by different individuals within the payment plan"
    default_severity = "medium"
    default_config = {"check_types": ["NATIONAL_ID", "PASSPORT", "SOCIAL_SECURITY"]}

    def evaluate(self, ctx: RuleContext) -> list[Finding]:
        doc_map: dict[str, list[dict]] = defaultdict(list)
        check_types = self.get_config(ctx).get("check_types", ["NATIONAL_ID", "PASSPORT", "SOCIAL_SECURITY"])

        for payment in ctx.payments:
            individuals = payment.get("snapshot_data", {}).get("individuals", [])
            for ind in individuals:
                for doc in ind.get("documents", []):
                    doc_type = doc.get("type", "")
                    doc_number = doc.get("document_number", "")
                    if doc_type in check_types and doc_number:
                        key = f"{doc_type}:{doc_number}"
                        doc_map[key].append(
                            {
                                "individual_id": str(ind.get("id", "")),
                                "individual_name": ind.get("full_name", ""),
                                "household": payment.get("household_unicef_id", ""),
                                "doc_type": doc_type,
                                "doc_number": doc_number,
                            }
                        )

        findings = []
        for entries in doc_map.values():
            if len(entries) > 1:
                unique_individuals = {e["individual_id"] for e in entries}
                if len(unique_individuals) > 1:
                    doc_type = entries[0]["doc_type"]
                    doc_number = entries[0]["doc_number"]
                    names = ", ".join(f"{e['individual_name']} ({e['household']})" for e in entries)
                    findings.append(
                        Finding(
                            severity=self.default_severity,
                            title=f"{doc_type} {doc_number} used by {len(unique_individuals)} individuals",
                            description=f"Document {doc_type} {doc_number} is shared by: {names}",
                            object_type="individual",
                            object_id="",
                            object_unicef_id="",
                            metadata={"document_type": doc_type, "document_number": doc_number, "entries": entries},
                        )
                    )
        return findings
