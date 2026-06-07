# POST /api/run/ — Submit a PaymentPlan for analysis

Triggers anomaly detection on a PaymentPlan. Data is pushed by HOPE via API payload.

## Request

Authentication: `Authorization: Bearer <AMS_API_KEY>`

```json
{
  "branch": "prevention",
  "callback_url": "https://hope.unicef.org/api/ams-callback/",
  "payment_plan": {
    "id": "3a4b8c91-d7e2-4f6a-9b0c-1d2e3f4a5b6c",
    "unicef_id": "PP-20-00042",
    "business_area": {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "name": "Ukraine",
      "slug": "ukr"
    },
    "program": {
      "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
      "name": "MPC Winter 2026"
    },
    "status": "LOCKED",
    "dispersion_start_date": "2026-06-01",
    "currency": "USD",
    "total_entitled_quantity": 1250000.00,
    "delivery_mechanism": "Cash",
    "financial_service_provider": "Western Union",
    "reconciliation_window_in_days": 90,
    "payments": [
      {
        "id": "f0e1d2c3-b4a5-6789-0fed-cba987654321",
        "unicef_id": "PAY-20-00001",
        "household_id": "c4d5e6f7-a8b9-0123-cdef-456789012345",
        "household_unicef_id": "HH-20-00134",
        "status": "Pending",
        "entitlement_quantity": 7500.00,
        "entitlement_quantity_usd": 7500.00,
        "delivered_quantity": null,
        "delivered_quantity_usd": null,
        "delivery_date": null,
        "financial_service_provider": "Western Union",
        "delivery_type": "Cash",
        "currency": "USD",
        "excluded": false,
        "conflicted": false,
        "vulnerability_score": 5.5,
        "order_number": 1,
        "token_number": "",
        "snapshot_data": {
          "id": "c4d5e6f7-a8b9-0123-cdef-456789012345",
          "unicef_id": "HH-20-00134",
          "size": 5,
          "admin1": "Odeska oblast",
          "admin2": "Odesa",
          "address": "12 Main Street, Apt 3",
          "residence_status": "refugee",
          "withdrawn": false,
          "first_registration_date": "2025-11-01",
          "last_registration_date": "2026-02-15",
          "primary_collector": {
            "id": "d5e6f7a8-b9c0-1234-def0-567890123456",
            "unicef_id": "IND-20-00512",
            "full_name": "Olena Petrenko",
            "relationship": "HEAD",
            "sex": "FEMALE",
            "birth_date": "1985-03-22",
            "estimated_birth_date": false,
            "phone_no": "+380501234567",
            "disability": "NONE",
            "sanction_list_confirmed_match": false,
            "documents": [
              {
                "type": "NATIONAL_ID",
                "document_number": "UA123456",
                "expiry_date": "2030-01-01",
                "country": "UKR",
                "status": "VALID",
                "cleared": true
              }
            ],
            "account_data": {
              "number": "UA2132231300000260075671",
              "financial_institution_name": "PrivatBank"
            }
          },
          "individuals": [
            {
              "id": "d5e6f7a8-b9c0-1234-def0-567890123456",
              "unicef_id": "IND-20-00512",
              "full_name": "Olena Petrenko",
              "relationship": "HEAD",
              "sex": "FEMALE",
              "birth_date": "1985-03-22",
              "estimated_birth_date": false,
              "phone_no": "+380501234567",
              "pregnant": false,
              "disability": "NONE",
              "sanction_list_confirmed_match": false,
              "sanction_list_possible_match": false,
              "wallet_address": "",
              "documents": [
                {
                  "type": "NATIONAL_ID",
                  "document_number": "UA123456",
                  "expiry_date": "2030-01-01",
                  "country": "UKR",
                  "status": "VALID"
                }
              ]
            },
            {
              "id": "f6a7b8c9-d0e1-3456-f012-789012345678",
              "unicef_id": "IND-20-00514",
              "full_name": "Ivan Petrenko",
              "relationship": "SON_DAUGHTER",
              "sex": "MALE",
              "birth_date": "2015-07-15",
              "estimated_birth_date": false,
              "phone_no": "",
              "documents": []
            },
            {
              "id": "b8c9d0e1-f2a3-5678-1234-901234567890",
              "unicef_id": "IND-20-00516",
              "full_name": "Petro Petrenko",
              "relationship": "HEAD",
              "sex": "MALE",
              "birth_date": "1983-07-10",
              "estimated_birth_date": false,
              "disability": "DISABLED",
              "observed_disability": ["physical_disability"],
              "phone_no": "+380509876543",
              "sanction_list_confirmed_match": false,
              "documents": [
                {
                  "type": "NATIONAL_ID",
                  "document_number": "UA789012",
                  "expiry_date": "2032-05-15",
                  "country": "UKR",
                  "status": "VALID"
                }
              ]
            }
          ]
        },
        "verification": null,
        "current_household_data": null
      }
    ]
  },
  "config": {}
}
```

## Response (202)

```json
{
  "run_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "queued",
  "eta_seconds": 30
}
```

## Field reference

### Branch

| Value | Description |
|-------|-------------|
| `prevention` | Run before disbursement, on pending/frozen data |
| `detection` | Run after reconciliation, with verification data |

### PaymentPlan fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | UUID | yes | Same ID as HOPE's PaymentPlan |
| `unicef_id` | string | no | Human-readable ID (e.g. "PP-20-00042") |
| `business_area` | object | yes | `{ id, name, slug }` |
| `program` | object | yes | `{ id, name }` |
| `status` | string | no | PaymentPlan status (e.g. "LOCKED") |
| `dispersion_start_date` | string | no | ISO date |
| `currency` | string | no | ISO currency code |
| `total_entitled_quantity` | number | no | Total amount |
| `delivery_mechanism` | string | no | e.g. "Cash" |
| `financial_service_provider` | string | no | e.g. "Western Union" |
| `reconciliation_window_in_days` | integer | no | Window for detection checks |
| `payments` | array | yes | List of payment objects |

### Payment fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | UUID | yes | Same ID as HOPE's Payment |
| `unicef_id` | string | no | Human-readable ID |
| `household_id` | UUID | no | Household UUID |
| `household_unicef_id` | string | no | Household human-readable ID |
| `status` | string | no | Payment status |
| `entitlement_quantity` | number | no | Entitled amount |
| `entitlement_quantity_usd` | number | no | Entitled amount in USD |
| `delivered_quantity` | number | no | Delivered amount (null if not yet delivered) |
| `delivered_quantity_usd` | number | no | Delivered amount in USD |
| `delivery_date` | string | no | ISO date of delivery |
| `financial_service_provider` | string | no | FSP name |
| `delivery_type` | string | no | Delivery mechanism code |
| `currency` | string | no | ISO currency code |
| `excluded` | boolean | no | Whether payment is excluded |
| `conflicted` | boolean | no | Whether payment has conflicts |
| `vulnerability_score` | number | no | HH vulnerability score |
| `order_number` | integer | no | Payment order |
| `token_number` | string | no | Payment token |
| `snapshot_data` | object | no | Frozen household + individual data |
| `verification` | object | no | Verification result (detection branch only) |
| `current_household_data` | object | no | Live household data for comparison (detection branch) |

### snapshot_data structure

The `snapshot_data` contains all Household and Individual model fields frozen at the time of PaymentPlan creation. See [How data is frozen](../integration.md#how-data-is-frozen) for details.

Fields commonly read by AMS rules:

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Household UUID |
| `unicef_id` | string | Household human-readable ID |
| `size` | int | Number of household members |
| `admin1` | string | Admin level 1 (region) |
| `admin2` | string | Admin level 2 (district) |
| `address` | string | Household address |
| `residence_status` | string | e.g. "refugee", "host" |
| `withdrawn` | bool | Whether household is withdrawn |
| `first_registration_date` | string | ISO date of first registration |
| `last_registration_date` | string | ISO date of last update |
| `primary_collector` | object | Full individual snapshot of primary collector |
| `alternate_collector` | object | Full individual snapshot of alternate collector |
| `roles` | array | List of { role, individual } |
| `individuals` | array | Full individual snapshots of all members |

Each individual inside `individuals[]`:
| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Individual UUID |
| `unicef_id` | string | Human-readable ID |
| `full_name` | string | Full name |
| `birth_date` | string | ISO date |
| `estimated_birth_date` | bool | Whether birth date is estimated |
| `age_at_registration` | int | Age at registration |
| `sex` | string | "MALE", "FEMALE", or "OTHER" |
| `relationship` | string | e.g. "HEAD", "SON_DAUGHTER" |
| `phone_no` | string | Primary phone number |
| `phone_no_alternative` | string | Alternative phone number |
| `payment_delivery_phone_no` | string | Delivery-specific phone number |
| `pregnant` | bool | Pregnancy status |
| `disability` | string | Disability status |
| `observed_disability` | array | List of observed disabilities |
| `sanction_list_confirmed_match` | bool | Confirmed sanction list match |
| `sanction_list_possible_match` | bool | Possible sanction list match |
| `wallet_address` | string | Blockchain wallet address |
| `documents` | array | List of { type, document_number, expiry_date, country, status } |
| `account_data` | object | Bank/wallet account data (collectors only) |
