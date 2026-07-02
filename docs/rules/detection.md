# Detection rules (15)

Run **after** payment reconciliation, with delivery and verification data.

| Rule | Severity | Description |
|------|----------|-------------|
| `delivered_vs_received_mismatch` | high | The delivered quantity differs from the received amount reported in payment verification |
| `duplicate_payment_same_cycle` | critical | Same household has multiple successful payments in the same payment plan cycle |
| `reconciliation_overdue` | high | Payment plan is in ACCEPTED status past its reconciliation window |
| `pending_payment_stale` | medium | Payment has been in a pending status for longer than the configured threshold |
| `unusual_payment_timing` | low | Payment delivery date is significantly outside the normal distribution |
| `fsp_high_failure_rate` | high | A Financial Service Provider has a high proportion of failed/undelivered payments |
| `data_changed_after_approval` | critical | Current household data differs from the frozen snapshot data (requires HOPE to provide current data) |
| `payment_amount_hh_size_mismatch` | medium | Per-capita payment amount deviates significantly from expected |
| `partial_delivery_pattern` | low | Systematic partial deliveries to households in the same admin area |
| `withdrawn_hh_in_active_plan` | critical | A withdrawn household appears in an active (non-FINISHED/CLOSED) payment plan |
| `empty_household_active` | high | Household has zero members but appears in an active payment plan |
| `distributed_but_not_delivered` | high | Payment has a SUCCESS status but delivered_quantity is zero or null |
| `registration_date_anomaly` | medium | Program registration date is before the registration data import creation date |
| `unrealistic_sex_ratio` | medium | An admin area within the payment plan has an extreme male/female ratio |
| `pwd_prevalence_outlier` | low | Prevalence of Persons with Disabilities (PwD) differs significantly from the expected rate |
