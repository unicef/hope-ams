# Settings

All configuration is via environment variables, loaded with `django-environ` + `django-smart-env`.

## Django

| Variable | Default | Description |
|----------|---------|-------------|
| `DJANGO_SETTINGS_MODULE` | required | Must be `hope_ams.config.settings` |
| `SECRET_KEY` | required | Django secret key |
| `DEBUG` | `False` | Enable debug mode |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | Comma-separated allowed hosts |
| `DATABASE_URL` | required | PostgreSQL connection string |
| `STATIC_ROOT` | required | Static files directory |

## Auth

| Variable | Default | Description |
|----------|---------|-------------|
| `HOPE_API_TOKEN` | required | Shared secret for API authentication |

## Cache & Queue

| Variable | Default | Description |
|----------|---------|-------------|
| `CACHE_URL` | required | Redis URL for caching |
| `CELERY_BROKER_URL` | required | Redis URL for Celery broker |

## Celery

| Variable | Default | Description |
|----------|---------|-------------|
| `CELERY_TASK_ALWAYS_EAGER` | `False` | Run tasks synchronously (for testing) |

## Sentry

| Variable | Default | Description |
|----------|---------|-------------|
| `SENTRY_DSN` | `""` | Sentry DSN for error tracking |
| `SENTRY_ENVIRONMENT` | `"development"` | Environment name in Sentry |

## Admin

| Variable | Default | Description |
|----------|---------|-------------|
| `ADMIN_EMAIL` | `""` | Superuser email |
| `ADMIN_PASSWORD` | `""` | Superuser password |
