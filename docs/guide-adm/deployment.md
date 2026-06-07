# Deployment

## Docker

The project includes a multi-stage `Dockerfile` and `compose.yaml` for local deployment.

```bash
# Build and start all services
docker compose up -d

# View logs
docker compose logs -f

# Run migrations
docker compose exec app uv run python manage.py migrate

# Create admin user
docker compose exec app uv run python manage.py createsuperuser
```

## Container structure

| Service | Image | Purpose |
|---------|-------|---------|
| `db` | postgres:16 | PostgreSQL database |
| `redis` | redis:7 | Cache and Celery broker |
| `app` | hope-ams | Django application server (gunicorn) |
| `celery` | hope-ams | Celery worker for rule execution |

## Kubernetes (AKS)

The recommended deployment target is Azure Kubernetes Service (AKS). Required resources:

- 2 CPU cores, 4 GB RAM per app replica
- PostgreSQL Flexible Server or Azure Cosmos DB for PostgreSQL
- Azure Cache for Redis
- Persistent volume for static files (optional)

## Environment variables

All settings must be configured via environment variables. See [Settings](settings.md) for the full reference.

### Required for deployment

```
DJANGO_SETTINGS_MODULE=hope_ams.config.settings
SECRET_KEY=<random-secret>
DATABASE_URL=postgres://user:pass@host:5432/ams
CACHE_URL=redis://host:6379/0
CELERY_BROKER_URL=redis://host:6379/0
AMS_API_KEY=<shared-secret>
ALLOWED_HOSTS=ams.unicef.org
```
