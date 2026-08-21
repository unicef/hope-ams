from uuid import UUID

from hope_ams.models.choices import Phase

from .base import BaseRule, Finding, RuleContext


class MissingIdentityDataRule(BaseRule):
    name = "missing_identity_data"
    verbose_name = "Missing Minimum Identity Data"
    phases = [Phase.PREVENTION]
    default_severity = "high"
    description = "An individual in the payment household is missing required identity fields"
    default_config = {
        "required_individual_fields": ["full_name", "birth_date", "sex"],
        "require_document": True,
    }

    def evaluate(self, ctx: RuleContext) -> list[Finding]:
        findings = []
        cfg = self.get_config(ctx)
        required_fields: list[str] = cfg.get("required_individual_fields", ["full_name", "birth_date", "sex"])
        require_document: bool = cfg.get("require_document", True)

        for payment in ctx.payments:
            individuals = payment.get("snapshot_data", {}).get("individuals", [])
            for ind in individuals:
                missing = [f for f in required_fields if not ind.get(f)]
                if require_document and not ind.get("documents"):
                    missing.append("document")
                if not missing:
                    continue
                findings.append(
                    Finding(
                        severity=self.default_severity,
                        title=f"Individual missing required fields: {', '.join(missing)}",
                        description=(
                            f"Individual {ind.get('unicef_id', ind.get('id', ''))} "
                            f"(household {payment.get('household_unicef_id', '')}) "
                            f"is missing: {', '.join(missing)}"
                        ),
                        object_type="individual",
                        object_id=UUID(str(ind.get("id", ""))),
                        object_unicef_id=str(ind.get("unicef_id", "")),
                        metadata={
                            "missing_fields": missing,
                            "household_unicef_id": payment.get("household_unicef_id"),
                        },
                        payment_id=payment.get("id"),
                        household_id=payment.get("household_id"),
                        individual_id=ind.get("id"),
                    )
                )
        return findings
