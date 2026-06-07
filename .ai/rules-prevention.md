# Prevention Rules (15)

Run pre-payment to catch issues before money is sent.

| # | Rule | Severity | What it checks |
|---|---|---|---|
| 1 | child_head_of_household | high | HoH age < 18 |
| 2 | unrealistic_age | critical | Age > 110 or birth_date in future |
| 3 | phone_number_reuse | high | Same phone across different households in same PP |
| 4 | same_wallet_multiple_households | high | Shared wallet_address across households |
| 5 | excessive_household_size | medium | Size > configurable threshold (default: 15) |
| 6 | no_working_age_adults | high | Zero 18–59-year-olds with >3 children |
| 7 | entitlement_outlier | medium | Entitlement > mean + 3σ for the PP |
| 8 | zero_entitlement_not_excluded | high | entitlement=0 but excluded=false |
| 9 | missing_collector | high | No PRIMARY or ALTERNATE collector in roles |
| 10 | collector_equals_beneficiary | low | Collector is also the head of household |
| 11 | document_cross_program | medium | Same doc number, different individuals |
| 12 | same_address_different_heads | medium | Same address, different heads of household |
| 13 | sanction_list_cross_ref | critical | Individual confirmed on sanction list |
| 14 | pregnant_child | critical | Pregnant and age < 12 or > 55 |
| 15 | estimated_birth_date_mismatch | medium | estimated_birth_date=true but age_at_registration ≠ calculated age |
