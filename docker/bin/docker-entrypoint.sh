#!/bin/sh -e

export UWSGI_PROCESSES="${UWSGI_PROCESSES:-"4"}"
export DJANGO_SETTINGS_MODULE="hope_ams.config.settings"

mkdir -p /app/
chown -R hope:unicef /app
cd /app

case "$1" in
    run)
      django-admin upgrade --with-check
      exec uwsgi --http :8000 \
        -H /venv \
        --module hope_ams.config.wsgi \
        --mimefile=/conf/mime.types \
        --uid hope \
        --gid unicef \
        --buffer-size 8192 \
        --http-buffer-size 8192
      ;;
    upgrade)
      django-admin upgrade --with-check
      ;;
    worker)
      shift
      exec gosu hope:unicef celery -A hope_ams.config.celery worker -E --loglevel=INFO "$@"
      ;;
    beat)
      shift
      exec gosu hope:unicef celery -A hope_ams.config.celery beat --loglevel=INFO \
        --scheduler django_celery_beat.schedulers:DatabaseScheduler "$@"
      ;;
    dev)
      django-admin collectstatic --no-input
      django-admin migrate
      exec django-admin runserver 0.0.0.0:8000
      ;;
    *)
      exec "$@"
      ;;
esac
