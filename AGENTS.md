# AMS — Agent Guidance

## Quick start

```bash
uv sync --frozen
cp .envrc .envrc && direnv allow
uv run python manage.py migrate
uv run python manage.py runserver
```

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

## Commands

| what | command |
|---|---|
| lint | `tox -e lint` |
| typecheck | `tox -e mypy` |
| tests | `uv run tox -e tests -- pytest tests -q` |
| migrate | `uv run python manage.py migrate` |
| shell | `uv run python manage.py shell` |
| docs (dev) | `uv sync --group docs && zensical serve` |
| docs (build) | `uv sync --group docs && zensical build` |

## Architecture

- **Package**: `hope_ams`, source in `src/hope_ams/`
- **Settings**: `hope_ams.config.settings` with `SmartEnv` + fragments
- **Celery**: `hope_ams.config.celery` app
- **API**: DRF views at `hope_ams.api.views`
- **Detections**: Core domain in `hope_ams.detections`

## Rule structure

Each rule is a class inheriting `BaseRule` with `evaluate(RuleContext) -> list[Finding]`.
Rules auto-register via `registry.register()` in `__init__.py`.

## CI/CD

| Workflow | Trigger | Jobs |
|----------|---------|------|
| `ci-pr.yml` | PR → develop/main | lint + mypy + tests |
| `ci-cd.yml` | Push → develop/main | lint → tests → sdlc-push |
| `sdlc-push.yml` | Push → **any** | Buildx + push to Docker Hub |
| `sdlc-version-create.yml` | Tag semver | Buildx + push with version tag |
| `release.yml` | GitHub Release | Buildx stage=dist + push |
| `docs.yml` | Push develop + schedule | Zensical build → GitHub Pages |

**Key vars/secrets needed:**
- `secrets.DOCKERHUB_USERNAME` / `secrets.DOCKERHUB_TOKEN` — Docker Hub login
- `secrets.DOCKERHUB_ORGANIZATION` (vars) — Docker Hub org (default: `unicef`)
