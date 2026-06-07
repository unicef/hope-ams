INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "hope_ams.apps.HopeAMSAdminConfig",
    "rest_framework",
    "django_celery_results",
    "hope_ams.apps.HopeAMSConfig",
    "hope_ams.detections.apps.Config",
    "hope_ams.api.apps.Config",
    "hope_ams.contrib.hope.apps.Config",
]
