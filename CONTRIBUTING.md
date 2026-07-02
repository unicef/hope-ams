# Contributing to HOPE AMS

## Quick start

```bash
uv sync --frozen
cp .envrc .envrc && direnv allow
uv run python manage.py migrate
uv run python manage.py runserver
```

## Commands

| What | Command |
|---|---|
| lint | `tox -e lint` |
| typecheck | `tox -e mypy` |
| tests | `uv run tox -e tests -- pytest tests -q` |
| migrate | `uv run python manage.py migrate` |
| shell | `uv run python manage.py shell` |
| env — check | `uv run python manage.py env --check` |
| env — develop | `uv run python manage.py env --develop` |
| docs (dev) | `uv sync --group docs && zensical serve` |
| docs (build) | `uv sync --group docs && zensical build` |

## Docker

```bash
# Build
docker build -f docker/Dockerfile --target dist -t hope-ams .

# Run (uwsgi)
docker run -e DATABASE_URL=... -e SECRET_KEY=... hope-ams

# Run (dev server)
docker run -e ... hope-ams dev

# Run (celery worker)
docker run -e ... hope-ams worker

# Run tests
docker build -f docker/Dockerfile --target tests -t hope-ams-tests .
docker run --network host -v ./src:/app/src -v ./tests:/app/tests hope-ams-tests \
  pytest tests -q
```

## Configuration

Environment variables are managed via [`django-smart-env`](https://github.com/unicef/django-smart-env).
Variables are declared in `src/hope_ams/config/__init__.py` as 5-tuples:

```python
(cast, default, develop_value, is_explicit, help_text)
```

Variables marked **explicit** are required — Django's check framework raises
`smart_env.E001` if missing.

Generate `.envrc` from the config:

```bash
uv run python manage.py env --develop --format 'export {key}={value}' > .envrc
```

Edit `.envrc` to fill in secrets (`HOPE_API_TOKEN`, `DATABASE_URL`, `SENTRY_DSN`, …),
run `direnv allow`, then verify with `uv run python manage.py env --check`.

## Architecture

- **Package**: `hope_ams`, source in `src/hope_ams/`
- **Settings**: `hope_ams.config.settings` with `SmartEnv` + fragments
- **Celery**: `hope_ams.config.celery` app
- **API**: DRF views at `hope_ams.api.views`
- **Detections**: Core domain in `hope_ams.detection`

No database access to HOPE — all data is pushed via API.
Rule config hierarchy: Global → BusinessArea → Program → PaymentPlan.
Auth: Static API key (`Authorization: Bearer <key>`).

## Two branches

| Branch | When | What it checks |
|---|---|---|
| **Prevention** | Pre-payment (PP → OPEN/LOCKED/ACCEPTED) | Data quality, duplicates, entitlements |
| **Detection** | Post-reconciliation (PP → FINISHED) | Payment outliers, fraud patterns |

## Flow

```
HOPE ──POST /api/run/──→ AMS ──callback──→ HOPE ──GET /api/anomalies/──→ AMS
```

## Adding a rule

Each rule inherits `BaseRule` with `evaluate(RuleContext) -> list[Finding]`.
Rules auto-register via `registry.register()` in `__init__.py`.

See [docs/guide-contrib/adding-a-rule.md](docs/guide-contrib/adding-a-rule.md) for the full guide.

## CI/CD

| Workflow | Trigger | Jobs |
|---|---|---|
| `ci-pr.yml` | PR → develop/main | lint + mypy + tests |
| `ci-cd.yml` | Push → develop/main | lint → tests → sdlc-push |
| `sdlc-push.yml` | Push → any | Buildx + push to Docker Hub |
| `sdlc-version-create.yml` | Tag semver | Buildx + push with version tag |
| `release.yml` | GitHub Release | Buildx stage=dist + push |
| `docs.yml` | Push develop + schedule | Zensical build → GitHub Pages |

**Secrets required:**
- `DOCKERHUB_USERNAME` / `DOCKERHUB_TOKEN` — Docker Hub login
- `DOCKERHUB_ORGANIZATION` — Docker Hub org (default: `unicef`)

## Pull request guidelines

1. Branch from `develop` and open PRs against `develop`.
2. Keep changes focused — one feature/fix per PR.
3. Run `tox -e lint` and `tox -e mypy` before pushing.
4. Ensure tests pass (`uv run tox -e tests -- pytest tests -q`).
5. Update or add tests for new functionality.
6. Update Zensical docs if changing public API or behaviour.
