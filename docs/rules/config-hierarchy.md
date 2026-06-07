# Rule config hierarchy

Configuration is resolved at multiple levels, from most general to most specific:

## Resolution order

```
1. Rule.default_config          (hardcoded in the rule class)
2. Global RuleConfig            (scope=global)
3. BusinessArea RuleConfig      (scope=business_area, matched by BA ID)
4. Program RuleConfig           (scope=program, matched by program ID)
5. PaymentPlan RuleConfig       (scope=payment_plan, matched by PP ID)
6. Runtime overrides            (config.rules.rule_name in API payload)
```

At each level, values from the more specific override win.

## Example

```python
# Rule default
default_config = {"max_age": 120, "max_size": 15}

# Global config
{"max_age": 110}

# BusinessArea config (Ukraine)
{"max_size": 10}

# Runtime override in API payload
config = {
    "rules": {
        "unrealistic_age": {
            "enabled": True,
            "config": {"max_age": 100}
        }
    }
}

# Result for Ukraine BA:
# max_age = 100 (runtime override)
# max_size = 10 (BA-level config)
```

## Admin management

RuleConfig records can be created via the Django admin interface at `/admin/detections/ruleconfig/`.

Available scopes:

| Scope | Effect |
|-------|--------|
| `global` | Applies to all BusinessAreas |
| `business_area` | Applies to a specific BA |
| `program` | Applies to a specific program within a BA |
| `payment_plan` | Applies to a specific PaymentPlan |
