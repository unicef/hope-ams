# Rule Configuration Hierarchy

Rules can be enabled/disabled at 4 levels. Each level overrides the parent.

## Priority (1 = highest)

1. **PaymentPlan** — overrides Program, BA, Global
2. **Program** — overrides BA, Global
3. **BusinessArea** — overrides Global
4. **Global** — default for everything

## Resolution function

```python
def resolve_rule_config(rule_name, payment_plan):
    """Walk hierarchy from most to least specific."""
    qs = RuleConfig.objects.filter(rule_name=rule_name)

    config = qs.filter(scope="payment_plan", payment_plan=payment_plan).first()
    if config: return config

    config = qs.filter(scope="program", program=payment_plan.program).first()
    if config: return config

    config = qs.filter(scope="business_area", business_area=payment_plan.business_area).first()
    if config: return config

    return qs.filter(scope="global").first()
```

## Admin management

All RuleConfig entries are managed via Django admin:
- Filterable by `scope`, `rule_name`, `business_area`
- Each RuleConfig has `enabled` toggle and `config` JSON field for thresholds

## Default behavior

When no RuleConfig exists for a rule, the rule runs with its built-in default thresholds (from `BaseRule.default_config`). To disable a rule globally, create a Global RuleConfig with `enabled=false`.
