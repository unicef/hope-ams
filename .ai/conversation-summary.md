# Conversation Summary — AMS Design Session

## Date
2026-06-07

## Key Decisions

| Decision | Choice |
|---|---|
| System type | Standalone Django microservice |
| Location | `/Users/sax/Documents/data/PROGETTI/UNICEF/hct-mis/ams/` |
| Package name | `hope_ams` |
| Structure mirrors | `hope-country-workspace` |
| Database access to HOPE | **None** — all data pushed via API |
| Data source | Frozen `PaymentHouseholdSnapshot.snapshot_data` sent in request body |
| Trigger | HOPE calls POST /api/run/ when PaymentPlan status changes |
| Feedback | Callback pattern: AMS calls HOPE's URL → HOPE pulls results from AMS |
| Branches | **Prevention** (pre-payment) + **Detection** (post-reconciliation) |
| Auth | Static API key in `Authorization: Bearer` header |
| Frontend | Django templates (no SPA) |
| AMS is | **Advisory only** — HOPE decides how to use findings |
| Rule config | Hierarchical: Global → BusinessArea → Program → PaymentPlan |
| Rule config stored | In AMS local DB (not HOPE) |
| No unused modules | Stripped-down structure, no middleware/security/versioning/cache stubs |

## Architecture Pattern

```
HOPE ──POST /api/run/──→ AMS ──callback──→ HOPE ──GET /api/anomalies/──→ AMS
```

## Related projects

- `hope-ads` exists at `/Users/sax/Documents/data/PROGETTI/UNICEF/hope-ads/` (ML project, not Django — not used)
- Reference: `hope-country-workspace` at `/Users/sax/Documents/data/PROGETTI/UNICEF/hope-country-workspace/`
