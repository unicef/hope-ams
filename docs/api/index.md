# API

All API endpoints require authentication via `Authorization: Bearer <AMS_API_KEY>` header.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/run/` | Submit a PaymentPlan for analysis |
| `GET` | `/api/runs/{id}/` | Check run status |
| `GET` | `/api/anomalies/` | List/query anomaly findings |
| `PATCH` | `/api/anomalies/{id}/` | Update anomaly status |
| `GET` | `/api/stats/` | Dashboard statistics |
| `GET` | `/api/rules/` | List rule configurations |
