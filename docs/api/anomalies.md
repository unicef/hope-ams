# GET /api/anomalies/ — Retrieve findings

List anomaly findings with optional filters.

## Query parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `run_id` | UUID | Filter by detection run |
| `branch` | string | `prevention` or `detection` |
| `severity` | string | `low`, `medium`, `high`, `critical` |
| `status` | string | `open`, `reviewing`, `dismissed`, `confirmed` |
| `rule_name` | string | Filter by specific rule |
| `business_area_id` | UUID | Filter by business area |
| `page` | int | Page number (default: 1) |
| `page_size` | int | Items per page (default: 100) |

## Response

```json
{
  "count": 3,
  "results": [
    {
      "id": "uuid",
      "detection_run": "uuid",
      "branch": "prevention",
      "rule_name": "child_head_of_household",
      "severity": "high",
      "status": "open",
      "title": "Head of household is 14 years old",
      "description": "Household HH-20-0001 has head of household aged 14",
      "business_area": "uuid",
      "program": "uuid",
      "payment_plan": "uuid",
      "object_type": "household",
      "object_id": "uuid",
      "object_unicef_id": "HH-20-0001",
      "metadata": {
        "age": 14,
        "relationship": "HEAD",
        "individual_id": "uuid"
      },
      "created_at": "2026-06-01T10:00:15Z",
      "updated_at": "2026-06-01T10:00:15Z"
    }
  ]
}
```

# PATCH /api/anomalies/{id}/ — Update status

Update the status of an anomaly finding (e.g. confirm or dismiss).

## Request

```json
{
  "status": "confirmed"
}
```

Allowed status values: `open`, `reviewing`, `dismissed`, `confirmed`
