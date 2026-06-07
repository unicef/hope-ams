# Detection rules (15)

Run **after** payment reconciliation, with delivery and verification data.

| Rule | Severity | Description |
|------|----------|-------------|
| `delivered_vs_received_mismatch` | high | Detects discrepancies between delivered amount and verified received amount |
| `duplicate_payment_same_cycle` | critical | Detects same household receiving multiple payments in the same cycle |
| `reconciliation_overdue` | medium | Detects payments past their reconciliation window |
| `pending_payment_stale` | medium | Detects payments stuck in pending status beyond threshold |
| `unusual_payment_timing` | low | Detects payments made at unusual times (e.g. weekends, holidays) |
| `fsp_high_failure_rate` | high | Detects Financial Service Providers with unusually high failure rates |
| `data_changed_after_approval` | critical | Detects household data changes after payment plan approval |
| `payment_amount_hh_size_mismatch` | medium | Detects payments where amount doesn't match household size |
| `partial_delivery_pattern` | medium | Detects patterns of partial deliveries in an area |
| `withdrawn_hh_in_active_plan` | critical | Detects withdrawn households still active in a payment plan |
| `empty_household_active` | high | Detects active households with zero members |
| `distributed_but_not_delivered` | high | Detects payments marked as distributed but not delivered |
| `registration_date_anomaly` | low | Detects unusual registration date patterns |
| `unrealistic_sex_ratio` | medium | Detects households with unrealistic male/female ratios |
| `pwd_prevalence_outlier` | low | Detects households with unusually high/low disability prevalence |
