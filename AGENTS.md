# AMS — Agent Guidance

AMS is a standalone Django microservice that performs **rule-based anomaly detection** on HOPE payment data. It has zero access to HOPE databases — all data is pushed via API payload.

Python 3.14 · uv + tox · Django · DRF · Celery · PostgreSQL · Redis

## Quick start

```bash
uv sync --frozen
cp .envrc .envrc && direnv allow       # .envrc already provides defaults
uv run python manage.py migrate
uv run python manage.py runserver      # runs on 0.0.0.0:8000
```

**Compose mode** (db + redis + app + celery pre-wired):

```bash
docker compose up --build
```
Ports: PostgreSQL 5433, Redis 6380, app 8000.

## Code conventions

Check `.ai` folder for further requirements, specifications and directives.

## Architecture

- **Package**: `hope_ams`, source in `src/hope_ams/`
- **Settings**: `hope_ams.config.settings` — uses `django-smart-env` + fragment loading
- **Celery**: `hope_ams.config.celery` app (schedule managed via `django-celery-beat`)
- **API**: DRF views at `hope_ams.api.views`
- **Detections**: Core domain in `hope_ams.detection`
- **Build**: hatchling, version from git (`hatch-vcs`), package = `src/hope_ams`

## Rule engine

Each rule is a class inheriting `BaseRule` with `evaluate(RuleContext) -> list[Finding]`.
Rules auto-register via `registry.register()` in their module's `__init__.py`.

Two flows: **Analyse** (pre-payment anomaly detection) and **Detect** (post-payment).
