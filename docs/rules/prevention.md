# Prevention rules (15)

Run **before** payment disbursement, on pending/frozen data.

| Rule | Severity | Description |
|------|----------|-------------|
| `child_head_of_household` | high | Detects households where the head is under 18 |
| `unrealistic_age` | critical | Detects individuals with birth dates implying age > 120 or negative age |
| `pregnant_child` | critical | Detects children (under 18) marked as pregnant |
| `no_working_age_adults` | medium | Detects households with no adults aged 18-60 |
| `excessive_household_size` | medium | Detects households exceeding maximum size (configurable, default 20) |
| `zero_entitlement_not_excluded` | high | Detects payments with zero entitlement that are not excluded |
| `missing_collector` | high | Detects payments with no primary or alternate collector |
| `collector_equals_beneficiary` | medium | Detects cases where collector and beneficiary are the same person |
| `phone_number_reuse` | high | Detects phone numbers shared across multiple individuals |
| `document_cross_program` | high | Detects same document used across different programs |
| `same_wallet_multiple_households` | high | Detects wallet addresses shared across multiple households |
| `same_address_different_heads` | medium | Detects same address with different heads of household |
| `sanction_list_cross_ref` | critical | Detects individuals with sanction list matches |
| `estimated_birth_date_mismatch` | medium | Detects inconsistencies in estimated birth dates |
| `entitlement_outlier` | medium | Detects entitlement amounts outside expected range |
