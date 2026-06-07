# GET /api/stats/ — Dashboard statistics

Returns aggregate statistics for the AMS dashboard.

## Response

```json
{
  "total_runs": 42,
  "total_anomalies": 156,
  "by_severity": {
    "critical": 2,
    "high": 15,
    "medium": 43,
    "low": 96
  },
  "by_branch": {
    "prevention": 89,
    "detection": 67
  },
  "recent_runs": [
    {
      "id": "uuid",
      "branch": "prevention",
      "status": "completed",
      "rules_executed": 15,
      "anomalies_found": 3,
      "started_at": "...",
      "finished_at": "..."
    }
  ]
}
```
