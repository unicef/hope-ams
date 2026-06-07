from smart_env import SmartEnv

CONFIG: dict[str, tuple] = {
    "ALLOWED_HOSTS": (
        list,
        [],
        ["127.0.0.1", "localhost"],
        True,
        "@see https://docs.djangoproject.com/en/5.0/ref/settings/#allowed-hosts",
    ),
    "AMS_API_KEY": (str, "", "", True, "API key for HOPE to authenticate to AMS"),
    "CACHE_URL": (
        str,
        "redis://localhost:6379/0",
        "",
        True,
        "@see https://docs.djangoproject.com/en/5.0/ref/settings/#cache-url",
    ),
    "CELERY_BROKER_URL": (str, "", "", True, "@see https://docs.celeryq.dev/en/stable/userguide/configuration.html"),
    "CELERY_TASK_ALWAYS_EAGER": (bool, False, True, False, ""),
    "DATABASE_URL": (
        str,
        SmartEnv.NOTSET,
        SmartEnv.NOTSET,
        True,
        "@see https://django-environ.readthedocs.io/en/latest/types.html",
    ),
    "DEBUG": (bool, False, True, False, "@see https://docs.djangoproject.com/en/5.0/ref/settings/#debug"),
    "SECRET_KEY": (
        str,
        "",
        "super_secret_key_just_for_testing",
        True,
        "@see https://docs.djangoproject.com/en/5.0/ref/settings/#secret-key",
    ),
    "SENTRY_DSN": (str, "", "", False, "Sentry DSN"),
    "SENTRY_ENVIRONMENT": (str, "", "", False, "Sentry environment"),
    "STATIC_ROOT": (
        str,
        "/var/static",
        "/tmp/static",  # noqa: S108
        True,
        "@see https://docs.djangoproject.com/en/5.0/ref/settings/#static-root",
    ),
    "STATIC_URL": (str, "/static/", "/static/", False, ""),
    "TIME_ZONE": (str, "UTC", "UTC", False, ""),
}

env = SmartEnv(**CONFIG)
