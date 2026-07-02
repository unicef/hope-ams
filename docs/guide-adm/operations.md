# Operations

## Celery

AMS uses Celery for asynchronous rule execution.

### Queue management

```bash
# Check Celery worker status
celery -A hope_ams.config.celery inspect ping

# List active queues
celery -A hope_ams.config.celery inspect active

# View registered tasks
celery -A hope_ams.config.celery inspect registered
```

### Monitoring

- Celery task results are stored in the Django database (django-celery-results)
- Failed tasks automatically retry up to 3 times with 60-second delay
- Task monitoring available via `/admin/djcelery/` (if enabled)

## Sentry

Error tracking via Sentry SDK. Configure via:

- `SENTRY_DSN` — Your Sentry project DSN
- `SENTRY_ENVIRONMENT` — Environment tag (e.g. "production", "staging")

## Logging

Logs are sent to stdout/stderr for container environments. Key log sources:

| Source | Logger | Level |
|--------|--------|-------|
| API views | `hope_ams.api` | INFO |
| Rule execution | `hope_ams.detection.rules` | INFO, ERROR |
| Celery tasks | `hope_ams.detection.tasks` | INFO, ERROR |
| Callbacks | `hope_ams.detection.callback` | WARNING |
| All | root | WARNING |

## Database

### Migrations

```bash
uv run python manage.py migrate
```

### Backup

Standard PostgreSQL backup procedures apply:

```bash
pg_dump ams > ams_backup_$(date +%Y%m%d).sql
```

## Health check

Use `GET /api/stats/` as a basic health check. A successful response (200) with valid JSON indicates the service is running.
