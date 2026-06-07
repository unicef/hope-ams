# AMS Architecture

## Overview

AMS (Anomaly Management System) is a standalone Django microservice that performs rule-based anomaly detection on HOPE payment data. It has zero access to HOPE databases — all data is pushed via API.

## Flow

```
HOPE (PaymentPlan status change)
  │
  │ POST /api/run/
  │   { payment_plan: {...}, payments: [{...snapshot_data}, ...],
  │     branch: "prevention"|"detection", callback_url: "..." }
  │
  ▼
AMS
  1. Validate payload, create/update hierarchy refs (BA, Program, PP)
  2. Enqueue Celery task
  3. Run all enabled rules (in-memory, no DB reads)
  4. Store AnomalyResult in local DB
  5. POST {callback_url} → HOPE with run summary
  │
  │ HOPE pulls results
  │ GET /api/anomalies/?run_id=uuid
  │
  ▼
HOPE displays/acts on findings
```

## Two Branches

| Branch | Trigger | Data | Purpose |
|---|---|---|---|
| **Prevention** | PP → OPEN/LOCKED/ACCEPTED | Payments (Pending) + `snapshot_data` (frozen HH + individuals) | Catch issues before money is sent |
| **Detection** | PP → FINISHED | Same + delivered quantities + verification results | Detect fraud/errors after reconciliation |

## Key Decisions

- **No read-only replica** — AMS gets all data via API payload
- **Callback pattern** — AMS notifies HOPE when done; HOPE pulls results
- **Rule config hierarchy** — Global → BusinessArea → Program → PaymentPlan
- **Static API key auth** — simple shared secret in header
- **Advisory only** — AMS reports findings; HOPE decides what to do
- **Django templates** — no separate frontend build
