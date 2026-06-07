# Detection Rules (15)

Run post-reconciliation to detect fraud, errors, and operational issues.

| # | Rule | Severity | What it checks |
|---|---|---|---|
| 1 | delivered_vs_received_mismatch | high | delivered_quantity ≠ received_amount |
| 2 | fsp_high_failure_rate | high | FSP has >20% failed payments in a PP |
| 3 | duplicate_payment_same_cycle | critical | Two SUCCESS payments for same HH in same cycle |
| 4 | payment_amount_hh_size_mismatch | medium | Per-capita amount far from expected |
| 5 | data_changed_after_approval | critical | Snapshot vs current household data differs significantly |
| 6 | withdrawn_hh_in_active_plan | critical | Withdrawn HH appears in active PP |
| 7 | reconciliation_overdue | high | PP ACCEPTED past its reconciliation window |
| 8 | pending_payment_stale | medium | Payment stuck in PENDING > N days |
| 9 | partial_delivery_pattern | low | Systematically partial deliveries to same admin area |
| 10 | distributed_but_not_delivered | high | Status=SUCCESS but delivered_quantity=0 |
| 11 | unrealistic_sex_ratio | medium | Admin area with extreme M/F ratio |
| 12 | pwd_prevalence_outlier | low | Disability % far from expected (15% global avg) |
| 13 | empty_household_active | high | size=0 but status active |
| 14 | registration_date_anomaly | medium | Program registration date before RDI creation date |
| 15 | unusual_payment_timing | low | Delivery date far outside normal distribution |
