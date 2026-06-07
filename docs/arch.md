# Architecture

## Overview

AMS is a standalone Django microservice that performs rule-based anomaly detection on HOPE payment data. It has zero access to HOPE databases — all data is pushed via API.

## System flow

```mermaid
sequenceDiagram
    participant H as HOPE
    participant A as AMS API
    participant C as AMS Celery
    participant D as AMS DB

    H->>A: POST /api/run/ (payload + callback_url)
    A->>D: Create/update BA, Program, PaymentPlan
    A->>D: Create DetectionRun (status=QUEUED)
    A->>C: process_analysis.delay(run_id, data)
    A-->>H: 202 { run_id, status: "queued" }

    C->>D: Set run status = RUNNING
    C->>C: Evaluate all enabled rules in-memory
    C->>D: Bulk create AnomalyResult records
    C->>D: Set run status = COMPLETED
    C->>H: POST {callback_url} (run summary)

    H->>A: GET /api/anomalies/?run_id=uuid
    A-->>H: { count, results: [...] }
```

## Two phases

| Phase | Trigger | Data | Purpose |
|--------|---------|------|---------|
| **Prevention** | PaymentPlan → OPEN/LOCKED/ACCEPTED | Payments (Pending) + `snapshot_data` (frozen HH + individuals) | Catch issues before money is sent |
| **Detection** | PaymentPlan → FINISHED | Same + delivered quantities + verification results | Detect fraud/errors after reconciliation |

## Key decisions

- **No read-only replica** — AMS gets all data via API payload
- **Callback pattern** — AMS notifies HOPE when done; HOPE pulls results
- **Rule config hierarchy** — Global → BusinessArea → Program → PaymentPlan
- **Static API key auth** — simple shared secret in header
- **Advisory only** — AMS reports findings; HOPE decides what to do
- **Django templates** — no separate frontend build (admin dashboard only)
