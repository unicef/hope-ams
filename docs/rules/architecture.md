# Rule architecture

## BaseRule

Every rule extends `BaseRule` (defined in `rules/base.py`):

```python
class BaseRule(ABC):
    name: str = ""                    # Auto-derived from class name
    branch: str = ""                  # "prevention" or "detection"
    description: str = ""             # Human-readable description
    default_severity: str = "medium"  # Default severity level
    default_config: dict = {}         # Default configuration parameters

    def get_config(self, ctx: RuleContext) -> dict:
        # Merged: default_config → DB RuleConfig → runtime overrides

    def is_enabled(self, ctx: RuleContext) -> bool:
        # Check if rule is enabled in current context

    @abstractmethod
    def evaluate(self, ctx: RuleContext) -> list[Finding]:
        # Core logic — return findings
```

## RuleContext

The context passed to every rule:

```python
@dataclass
class RuleContext:
    branch: str                    # "prevention" | "detection"
    payment_plan: dict             # PaymentPlan data from payload
    payments: list[dict]           # Payments array from payload
    config: dict                   # Runtime config overrides
    rule_config: dict | None       # Resolved DB RuleConfig (optional)

    @property
    def business_area_id(self) -> str
    @property
    def program_id(self) -> str
    @property
    def payment_plan_id(self) -> str
```

Rules access `snapshot_data` via `payment["snapshot_data"]` within each payment dict.

## Finding

The result of a rule evaluation:

```python
@dataclass
class Finding:
    severity: str                  # "low" | "medium" | "high" | "critical"
    title: str                     # Short summary
    description: str               # Detailed explanation
    object_type: str               # "household" | "individual" | "payment" | "payment_plan"
    object_id: UUID                # ID of the object with the issue
    object_unicef_id: str          # Human-readable ID
    metadata: dict                 # Rule-specific data (e.g. {"age": 14})
    payment_id: UUID | None
    household_id: UUID | None
    individual_id: UUID | None
```

## Registry

Rules auto-register via the `RuleRegistry` when imported. The registry provides:

- `registry.get_all(branch)` → all rules for a branch
- `registry.get_enabled(branch, config)` → enabled rules only (respecting runtime `config.rules.rule_name.enabled`)
- `registry.get_rule(name)` → single rule by name
