# API Contract

## Auth

All requests from HOPE include header:
```
Authorization: Bearer <AMS_API_KEY>
```

## Endpoints

### POST /api/run/ — Submit a PaymentPlan for analysis

Request:
```json
{
  "branch": "prevention",
  "callback_url": "https://hope.unicef.org/api/ams-callback/",
  "payment_plan": {
    "id": "uuid",
    "unicef_id": "PP-20-0001",
    "business_area": { "id": "uuid", "name": "Ukraine", "slug": "ukr" },
    "program": { "id": "uuid", "name": "MPC 2026" },
    "status": "OPEN",
    "dispersion_start_date": "2026-06-01",
    "currency": "USD",
    "total_entitled_quantity": 500000.00,
    "delivery_mechanism": "Cash",
    "financial_service_provider": "Western Union",
    "reconciliation_window_in_days": 90,
    "payments": [
      {
        "id": "uuid",
        "unicef_id": "PAY-001",
        "household_id": "uuid",
        "household_unicef_id": "HH-20-0001",
        "status": "Pending",
        "entitlement_quantity": 5000.00,
        "entitlement_quantity_usd": 5000.00,
        "delivered_quantity": null,
        "delivered_quantity_usd": null,
        "delivery_date": null,
        "financial_service_provider": "Western Union",
        "delivery_type": "Cash",
        "currency": "USD",
        "excluded": false,
        "conflicted": false,
        "vulnerability_score": 5.5,
        "order_number": 1,
        "token_number": "",
        "snapshot_data": { ... },
        "verification": null,
        "current_household_data": null
      }
    ]
  },
  "config": {}
}
```

Response (202):
```json
{
  "run_id": "uuid",
  "status": "queued",
  "eta_seconds": 30
}
```

### GET /api/runs/{id}/ — Check run status

Response:
```json
{
  "id": "uuid",
  "branch": "prevention",
  "status": "completed",
  "rules_executed": 15,
  "anomalies_found": 3,
  "started_at": "...",
  "finished_at": "..."
}
```

### GET /api/anomalies/ — Retrieve findings

Query params: `run_id`, `branch`, `severity`, `status`, `rule_name`, `business_area_id`

Response:
```json
{
  "count": 3,
  "results": [
    {
      "id": "uuid",
      "rule_name": "child_head_of_household",
      "severity": "high",
      "status": "open",
      "title": "Head of household is 14 years old",
      "description": "Household HH-20-0001 has head of household aged 14",
      "object_type": "household",
      "object_id": "uuid",
      "object_unicef_id": "HH-20-0001",
      "metadata": { "age": 14, "relationship": "HEAD" },
      "created_at": "..."
    }
  ]
}
```

### PATCH /api/anomalies/{id}/ — Update status

Body:
```json
{ "status": "confirmed" }
```

### GET /api/stats/ — Dashboard statistics

Response:
```json
{
  "total_runs": 42,
  "total_anomalies": 156,
  "by_severity": { "critical": 2, "high": 15, "medium": 43, "low": 96 },
  "by_branch": { "prevention": 89, "detection": 67 },
  "recent_runs": [...]
}
```
