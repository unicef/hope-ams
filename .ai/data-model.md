# Data Model

## Hierarchy (replicated from HOPE, populated lazily from API payloads)

```
BusinessArea (id, name, slug)
  └── Program (id, name, business_area FK)
       └── PaymentPlan (id, unicef_id, program FK, business_area FK)
```

## Rule Configuration

```
RuleConfig (rule_name, enabled, config JSON, scope, business_area FK, program FK, payment_plan FK)
```

Scope: global | business_area | program | payment_plan

Resolution order (most specific wins):
1. PaymentPlan-level
2. Program-level
3. BusinessArea-level
4. Global

## Detection Run

```
DetectionRun (id, branch, trigger, status, payment_plan FK, program FK, business_area FK,
              rules_executed, anomalies_found, started_at, finished_at, metadata JSON)
```

## Anomaly Result

```
AnomalyResult (id, detection_run FK, branch, rule_name, severity, status,
               title, description,
               business_area FK, program FK, payment_plan FK,
               object_type, object_id, object_unicef_id,
               metadata JSON, created_at, updated_at)
```
