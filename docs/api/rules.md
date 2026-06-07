# GET /api/rules/ — List rule configurations

Retrieve rule configurations with optional filters.

## Query parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `rule_name` | string | Filter by rule identifier |
| `scope` | string | `global`, `business_area`, `program`, `payment_plan` |

## Response

```json
[
  {
    "id": "uuid",
    "rule_name": "unrealistic_age",
    "enabled": true,
    "config": {
      "max_age": 120
    },
    "scope": "global",
    "business_area": null,
    "program": null,
    "payment_plan": null
  },
  {
    "id": "uuid",
    "rule_name": "excessive_household_size",
    "enabled": true,
    "config": {
      "max_size": 20
    },
    "scope": "business_area",
    "business_area": "uuid",
    "program": null,
    "payment_plan": null
  }
]
```
