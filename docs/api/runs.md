# GET /api/runs/{id}/ — Check run status

Retrieve the status and summary of a specific analysis run.

## Response

```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "branch": "prevention",
  "trigger": "api",
  "status": "completed",
  "payment_plan": "pp-id",
  "program": "prog-id",
  "business_area": "ba-id",
  "rules_executed": 15,
  "anomalies_found": 3,
  "started_at": "2026-06-01T10:00:00Z",
  "finished_at": "2026-06-01T10:00:15Z",
  "metadata": {
    "callback_url": "https://hope.unicef.org/api/ams-callback/"
  }
}
```
