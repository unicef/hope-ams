import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hope_ams.config.settings")

app = Celery("hope_ams")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
