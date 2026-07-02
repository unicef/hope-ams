# Prevention rules (15)

Run **before** payment disbursement, on pending/frozen data.

| Rule | Severity | Description |
|------|----------|-------------|
| `child_head_of_household` | high | Head of household is under 18 years old |
| `unrealistic_age` | critical | Individual has an unrealistic age (>110 or birth date in the future) |
| `pregnant_child` | critical | Individual is marked as pregnant but age is outside expected childbearing range |
| `no_working_age_adults` | high | Household has no working-age adults (18-59) with more than 3 children |
| `excessive_household_size` | medium | Household size exceeds configured maximum |
| `zero_entitlement_not_excluded` | high | Payment has zero entitlement but household is not marked as excluded |
| `missing_collector` | high | Household has no PRIMARY or ALTERNATE collector assigned |
| `collector_equals_beneficiary` | low | The payment collector is the same person as the head of household (potential conflict of interest flag) |
| `phone_number_reuse` | high | Same phone number used across different households in the same payment plan |
| `document_cross_program` | medium | Same identity document number used by different individuals within the payment plan |
| `same_wallet_multiple_households` | critical | Same wallet address used across different households |
| `same_address_different_heads` | medium | Multiple households share the same address but have different heads |
| `sanction_list_cross_ref` | critical | Individual has a confirmed sanction list match |
| `estimated_birth_date_mismatch` | medium | Birth date is estimated and age_at_registration doesn't match the calculated age from birth date |
| `entitlement_outlier` | medium | Payment entitlement quantity deviates significantly from the mean (outside N standard deviations) |
