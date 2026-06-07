# Running

## Development server

```bash
uv run python manage.py runserver
```

## Celery worker

```bash
uv run celery -A hope_ams.config.celery worker -l info
```

## Celery beat (scheduler)

```bash
uv run celery -A hope_ams.config.celery beat -l info
```

## Docker Compose

```bash
docker compose up
```

This starts:
- PostgreSQL
- Redis
- Django app (port 8000)
- Celery worker

## Admin interface

Available at `/admin/` with the Django admin credentials configured via environment variables.
