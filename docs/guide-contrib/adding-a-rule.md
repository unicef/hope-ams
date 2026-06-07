# Adding a rule

## Step 1: Create the rule file

Create a new file in the appropriate directory:

- Prevention: `src/hope_ams/detections/rules/prevention/<rule_name>.py`
- Detection: `src/hope_ams/detections/rules/detection/<rule_name>.py`

## Step 2: Implement the rule

```python
from __future__ import annotations

from uuid import UUID

from hope_ams.detections.rules.base import BaseRule, Finding, RuleContext


class MyNewRule(BaseRule):
    name = "my_new_rule"                        # Unique identifier
    branch = "prevention"                       # or "detection"
    description = "Detects something important" # Human-readable description
    default_severity = "high"                   # low | medium | high | critical
    default_config = {
        "max_threshold": 10,                    # Configurable parameters
        "min_threshold": 0,
    }

    def evaluate(self, ctx: RuleContext) -> list[Finding]:
        findings = []
        for payment in ctx.payments:
            snapshot = payment.get("snapshot_data", {})
            individuals = snapshot.get("individuals", [])
            for ind in individuals:
                # Your detection logic here
                if self._should_trigger(ind):
                    findings.append(Finding(
                        severity=self.default_severity,
                        title="Issue detected",
                        description=f"Individual {ind.get('unicef_id', 'unknown')} has an issue",
                        object_type="individual",
                        object_id=UUID(ind["id"]),
                        object_unicef_id=ind.get("unicef_id", ""),
                        metadata={"field": "value"},
                        individual_id=UUID(ind["id"]),
                        household_id=UUID(payment["household_id"]),
                        payment_id=UUID(payment["id"]),
                    ))
        return findings

    def _should_trigger(self, ind: dict) -> bool:
        config = self.get_config(ctx)  # ← merged config with overrides
        # Use config["max_threshold"], config["min_threshold"]
        ...
```

## Step 3: Register the rule

Add an import in the branch's `__init__.py`:

- Prevention: `src/hope_ams/detections/rules/prevention/__init__.py`
- Detection: `src/hope_ams/detections/rules/detection/__init__.py`

```python
from .my_new_rule import MyNewRule
```

Rules auto-register via the `RuleRegistry` when imported.

## Step 4: Add tests

Create or add to the test file:

```python
# tests/unit/test_rules_prevention.py

def test_my_new_rule(sample_payment: dict) -> None:
    from hope_ams.detections.rules.prevention.my_new_rule import MyNewRule

    ctx = RuleContext(
        branch="prevention",
        payment_plan=pp_data(),
        payments=[sample_payment],
    )
    findings = MyNewRule().evaluate(ctx)
    assert len(findings) == 1
    assert findings[0].severity == "high"
```

## Step 5: Update documentation

Add your rule to the appropriate catalog:

- `docs/rules/prevention.md` or `docs/rules/detection.md`
