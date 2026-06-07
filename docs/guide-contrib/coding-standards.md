# Coding standards

## Tools

| Tool | Purpose | Config file |
|------|---------|-------------|
| [ruff](https://docs.astral.sh/ruff/) | Linting + formatting | `ruff.toml` |
| [mypy](https://mypy-lang.org/) | Static type checking | `mypy.ini` |
| [pre-commit](https://pre-commit.com/) | Git hooks | `.pre-commit-config.yaml` |

## Commands

```bash
# Lint
tox -e lint         # ruff check + ruff format --check

# Type check
tox -e mypy

# Fix formatting
uv run ruff format src tests

# Auto-fix lint issues
uv run ruff check --fix src tests
```

## Conventions

- Python 3.14+ syntax
- Type annotations on all function signatures
- `from __future__ import annotations` at top of every file
- Django model fields with explicit `__str__`
- DRF serializers for API validation
- Dataclasses for internal data transfer (Finding, RuleContext)
- Celery tasks with `bind=True` and `max_retries`
- Tests use `pytest` with `django_db` marker

## Imports

Standard order (within each group, alphabetically):

1. `from __future__ import annotations`
2. Python standard library
3. Third-party packages
4. Django/DRF imports
5. Local application imports
