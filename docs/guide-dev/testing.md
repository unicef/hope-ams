# Testing

## Running tests

```bash
# Run all tests
uv run pytest tests -q

# Run specific test file
uv run pytest tests/unit/test_api.py -q

# Run tests with coverage
uv run pytest tests --cov=hope_ams -q

# Run tests matching a keyword
uv run pytest tests -q -k "child_head"
```

## Writing tests

Test fixtures are in `tests/unit/conftest.py` and include:

- `ba_data()` — BusinessArea payload dict
- `program_data()` — Program payload dict
- `pp_data()` — PaymentPlan payload dict
- `make_individual()` — Individual snapshot dict
- `sample_payment` — Realistic payment dict with nested `snapshot_data`
- `sample_submit_payload` — Full API payload for `POST /api/run/`

Example test:

```python
def test_unrealistic_age_rule(sample_payment: dict) -> None:
    ctx = RuleContext(
        branch="prevention",
        payment_plan=pp_data(),
        payments=[sample_payment],
    )
    ind = sample_payment["snapshot_data"]["individuals"][0]
    ind["birth_date"] = "1800-01-01"
    findings = UnrealisticAgeRule().evaluate(ctx)
    assert len(findings) == 1
    assert findings[0].severity == "critical"
```

## Tox

```bash
# Run all environments (lint, mypy, tests)
tox

# Run specific environment
tox -e tests
tox -e lint
tox -e mypy
```
