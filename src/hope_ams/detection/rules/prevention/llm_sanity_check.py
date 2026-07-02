import json

from hope_ams.detection.rules.base import Finding, RuleContext
from hope_ams.detection.rules.base_llm import BaseLLMRule


class LLMSanityCheckRule(BaseLLMRule):
    name = "llm_sanity_check"
    phase = "prevention"
    verbose_name = "LLM Sanity Check"
    description = "Uses a local LLM via Ollama to detect suspicious patterns in payment data"
    default_severity = "medium"
    system_prompt = (
        "You are a fraud detection expert analyzing HOPE payment data. Identify any suspicious or anomalous patterns."
    )

    def build_prompt(self, ctx: RuleContext) -> str:
        payment_summaries = []
        for p in ctx.payments[:20]:
            inds = p.get("snapshot_data", {}).get("individuals", [])
            payment_summaries.append(
                {
                    "id": str(p.get("id", "")),
                    "status": p.get("status"),
                    "entitlement_quantity": p.get("entitlement_quantity"),
                    "delivered_quantity": p.get("delivered_quantity"),
                    "household_size": len(inds),
                    "individuals": [
                        {
                            "age": i.get("age"),
                            "sex": i.get("sex"),
                            "disability": i.get("disability"),
                            "pregnant": i.get("pregnant"),
                        }
                        for i in inds
                    ],
                }
            )

        prompt = (
            f"Analyze the following {len(payment_summaries)} payments from "
            f"payment plan {ctx.payment_plan_id} "
            f"(office {ctx.office_id}, programme {ctx.programme_id}).\n\n"
        )
        prompt += json.dumps(payment_summaries, indent=2)
        prompt += (
            "\n\nReturn a JSON object with a 'findings' key containing an array of "
            "objects. Each object must have: "
            "'severity' ('low'|'medium'|'high'|'critical'), "
            "'title' (short description), "
            "'description' (detailed explanation), "
            "'object_type' ('household'|'individual'|'payment'|'payment_plan'), "
            "'object_id' (the UUID of the relevant entity). "
            "Return an empty array if nothing suspicious is found."
        )
        return prompt

    def parse_response(self, response: str) -> list[Finding]:
        data = json.loads(response)
        items = data.get("findings", [])
        return [Finding(**item) for item in items]
