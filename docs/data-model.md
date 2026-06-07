# Data model

## Hierarchy models (replicated from HOPE payload)

These models are created/updated via `update_or_create` from data in the API payload. AMS never queries HOPE's database.

### BusinessArea

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID (PK) | Same ID as HOPE's BusinessArea |
| `name` | CharField | Business area name (e.g. "Ukraine") |
| `slug` | CharField | URL-friendly slug |

### Program

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID (PK) | Same ID as HOPE's Program |
| `name` | CharField | Program name |
| `business_area` | FK → BusinessArea | Parent business area |

### PaymentPlan

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID (PK) | Same ID as HOPE's PaymentPlan |
| `unicef_id` | CharField | Human-readable ID (e.g. "PP-20-00042") |
| `program` | FK → Program | Parent program |
| `business_area` | FK → BusinessArea | Parent business area |

## Domain models (AMS-native)

### DetectionRun

Tracks each analysis execution.

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID (PK) | |
| `branch` | CharField | `prevention` or `detection` |
| `trigger` | CharField | `api` or `manual` |
| `status` | CharField | `queued` → `running` → `completed` / `failed` |
| `payment_plan` | FK → PaymentPlan | |
| `program` | FK → Program | |
| `business_area` | FK → BusinessArea | |
| `rules_executed` | IntegerField | Counter incremented per rule attempt |
| `anomalies_found` | IntegerField | Total findings for this run |
| `started_at` | DateTimeField | |
| `finished_at` | DateTimeField | nullable |
| `metadata` | JSONField | Contains `callback_url` and other runtime data |

### AnomalyResult

Individual findings produced by rules.

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID (PK) | |
| `detection_run` | FK → DetectionRun | Parent run |
| `branch` | CharField | `prevention` or `detection` |
| `rule_name` | CharField | Which rule produced this finding |
| `severity` | CharField | `low`, `medium`, `high`, `critical` |
| `status` | CharField | `open`, `reviewing`, `dismissed`, `confirmed` |
| `title` | CharField | Short summary (e.g. "Head of household is 14 years old") |
| `description` | TextField | Detailed explanation |
| `business_area` | FK → BusinessArea | |
| `program` | FK → Program | |
| `payment_plan` | FK → PaymentPlan | |
| `object_type` | CharField | `household`, `individual`, `payment`, `payment_plan` |
| `object_id` | UUIDField | ID of the object that triggered the finding |
| `object_unicef_id` | CharField | Human-readable ID of the object |
| `metadata` | JSONField | Rule-specific data (e.g. `{"age": 14, "relationship": "HEAD"}`) |
| `created_at` | DateTimeField | |
| `updated_at` | DateTimeField | |

### RuleConfig

Hierarchical rule configuration.

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID (PK) | |
| `rule_name` | CharField | Rule identifier (e.g. `unrealistic_age`) |
| `enabled` | BooleanField | Whether the rule is active |
| `config` | JSONField | Rule-specific parameters (thresholds, limits) |
| `scope` | CharField | `global`, `business_area`, `program`, `payment_plan` |
| `business_area` | FK → BusinessArea | nullable, set when scope = `business_area` |
| `program` | FK → Program | nullable, set when scope = `program` |
| `payment_plan` | FK → PaymentPlan | nullable, set when scope = `payment_plan` |

## Config hierarchy resolution

```
1. Start with rule's default_config
2. Merge Global RuleConfig (scope=global)
3. Merge BusinessArea RuleConfig (if matching BA)
4. Merge Program RuleConfig (if matching program)
5. Merge PaymentPlan RuleConfig (if matching PP)
6. Apply runtime overrides from config.rules.rule_name in the API payload
```

Most specific wins at each level.
