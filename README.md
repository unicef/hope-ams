# HOPE Anomaly Management System (AMS)

Standalone Django microservice for rule-based anomaly detection on HOPE payment data.

## Quick start

```bash
uv sync --frozen
uv run python manage.py env --develop --format 'export {key}={value}' > .envrc
# edit .envrc — fill in secrets (DB_URL, API keys, …)
direnv allow
uv run python manage.py migrate
uv run python manage.py runserver
```

## Configuration

Environment variables are managed via [`django-smart-env`](https://github.com/unicef/django-smart-env).
All variables are declared as 5-tuples in [`src/hope_ams/config/__init__.py`](src/hope_ams/config/__init__.py):

    (cast, default, develop_value, is_explicit, help_text)

Variables marked **explicit** are required — Django's `check` framework raises `smart_env.E001` if they are missing.

### Bootstrap your `.envrc`

Instead of maintaining a `.envrc.example` by hand, generate the skeleton from the config itself:

```bash
uv run python manage.py env --develop --format 'export {key}={value}' > .envrc
```

Then edit `.envrc` to fill in private values (`AMS_API_KEY`, `DATABASE_URL`, `SENTRY_DSN`, …),
run `direnv allow` to load them, and verify with `uv run python manage.py env --check`.

### Useful commands

| Command | What it does |
|---|---|
| `python manage.py env --check` | List any missing required (explicit) env vars |
| `python manage.py env --develop` | Dump all vars with their development defaults |
| `python manage.py env --changed` | Show vars whose current value differs from production default |
| `python manage.py env` | Print all vars with their current/resolved values |

## Two branches

| Branch | When | What it checks |
|---|---|---|
| **Prevention** | Pre-payment (PP → OPEN/LOCKED/ACCEPTED) | Data quality, duplicates, entitlements |
| **Detection** | Post-reconciliation (PP → FINISHED) | Payment outliers, fraud patterns |

## Flow

```
HOPE ──POST /api/run/──→ AMS ──callback──→ HOPE ──GET /api/anomalies/──→ AMS
```

## Architecture

- No database access to HOPE (all data pushed via API)
- Rule config hierarchy: Global → BusinessArea → Program → PaymentPlan
- Auth: Static API key (`Authorization: Bearer <key>`)
- Frontend: Django admin + template views
