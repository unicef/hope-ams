# HOPE Integration

Located in `HOPE/src/hope/apps/anomaly/`.

## Components

### models.py
- `PaymentPlanAMSStatus` — tracks last AMS run per PaymentPlan (run_id, status, anomalies_count, callback_received_at)

### signals.py
- `post_save PaymentPlan` — if BA has AMS enabled and status is OPEN/LOCKED/ACCEPTED/FINISHED, enqueue submission

### tasks.py
- `submit_to_ams(payment_plan_id)` — gathers data, builds payload, POSTs to AMS

### client.py
- `AMSClient` — HTTP wrapper with API key auth, methods: `submit_run()`, `get_findings()`

### views.py
- `POST /api/ams-callback/` — receives notification from AMS, updates PaymentPlanAMSStatus

## Payload Builder

```python
def build_ams_payload(pp, branch):
    payments = pp.payment_items.select_related(
        "household_snapshot", "delivery_type", "financial_service_provider"
    ).prefetch_related("payment_verifications")
    return {
        "branch": branch,
        "callback_url": f"{settings.BASE_URL}/api/ams-callback/",
        "payment_plan": {
            "id": str(pp.id),
            "unicef_id": pp.unicef_id,
            "business_area": {"id": str(pp.business_area.id), "name": pp.business_area.name, "slug": pp.business_area.slug},
            "program": {"id": str(pp.program_cycle.program.id), "name": pp.program_cycle.program.name},
            "status": pp.status,
            "dispersion_start_date": str(pp.dispersion_start_date),
            "currency": pp.currency,
            "total_entitled_quantity": float(pp.total_entitled_quantity),
            "delivery_mechanism": pp.delivery_mechanism.code,
            "financial_service_provider": pp.financial_service_provider.name,
            "reconciliation_window_in_days": pp.reconciliation_window_in_days,
            "payments": [                                          # ⬅ nested inside payment_plan
                {
                    "id": str(p.id),
                    "unicef_id": p.unicef_id,
                    "household_id": str(p.household_id),
                    "household_unicef_id": p.household.unicef_id,
                    "status": p.status,
                    "entitlement_quantity": float(p.entitlement_quantity),
                    "entitlement_quantity_usd": float(p.entitlement_quantity_usd),
                    "delivered_quantity": float(p.delivered_quantity) if p.delivered_quantity else None,
                    "delivered_quantity_usd": float(p.delivered_quantity_usd) if p.delivered_quantity_usd else None,
                    "delivery_date": str(p.delivery_date) if p.delivery_date else None,
                    "financial_service_provider": p.financial_service_provider.name if p.financial_service_provider else "",
                    "delivery_type": p.delivery_type.code if p.delivery_type else "",
                    "currency": p.currency.code if p.currency else "",
                    "excluded": p.excluded,
                    "conflicted": p.conflicted,
                    "vulnerability_score": float(p.vulnerability_score) if p.vulnerability_score else None,
                    "order_number": p.order_number,
                    "token_number": p.token_number or "",
                    "snapshot_data": p.household_snapshot.snapshot_data,   # ⬅ frozen data
                    "verification": serialize_verification(p) if branch == "detection" else None,
                    "current_household_data": None,
                }
                for p in payments
            ],
        },
        "config": {},
    }
```
