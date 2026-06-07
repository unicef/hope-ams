# HOPE AMS — Anomaly Management System

AMS is a standalone Django microservice that performs **rule-based anomaly detection** on HOPE payment data. It has zero access to HOPE databases — all data is pushed via API payload.

## Phases

| Phase | Trigger | Data | Purpose |
|--------|---------|------|---------|
| **Prevention** | PaymentPlan → OPEN/LOCKED/ACCEPTED | Payments (Pending) + `snapshot_data` (frozen HH + individuals) | Catch issues **before** money is sent |
| **Detection** | PaymentPlan → FINISHED | Same + delivered quantities + verification results | Detect fraud/errors **after** reconciliation |

## Quick start

```bash
uv sync --frozen
cp .envrc .envrc && direnv allow
uv run python manage.py migrate
uv run python manage.py runserver
```

## Flow

```mermaid
sequenceDiagram
    participant H as HOPE
    participant A as AMS API
    participant C as AMS Celery

    H->>A: POST /api/run/ (payload + callback_url)
    A->>C: process_analysis.delay()
    A-->>H: 202 { run_id, status: "queued" }

    C->>C: Evaluate rules in-memory
    C->>H: POST {callback_url} (run summary)

    H->>A: GET /api/anomalies/?run_id=uuid
    A-->>H: { count, results: [...] }
```

See [Architecture](arch.md) for the full sequence (including DB writes and status transitions).

## Key decisions

- **No read-only replica** — AMS gets all data via API payload
- **Callback pattern** — AMS notifies HOPE when done; HOPE pulls results
- **Rule config hierarchy** — Global → BusinessArea → Program → PaymentPlan
- **Static API key auth** — simple shared secret in header
- **Advisory only** — AMS reports findings; HOPE decides what to do
