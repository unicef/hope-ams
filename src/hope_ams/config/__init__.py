from typing import Any

from smart_env import SmartEnv

DJANGO_HELP_BASE = "https://docs.djangoproject.com/en/5.0/ref/settings"


def setting(anchor: str) -> str:
    return f"@see {DJANGO_HELP_BASE}#{anchor}"


CONFIG: dict[str, tuple[Any, ...]] = {
    "ALLOWED_HOSTS": (
        list,
        [],
        ["127.0.0.1", "localhost"],
        True,
        "@see https://docs.djangoproject.com/en/5.0/ref/settings/#allowed-hosts",
    ),
    "AMS_ANY_USER_AUTH_BACKEND": (
        bool,
        False,
        False,
        False,
        "Enable AnyUserAuthBackend so admin login works without creating users first",
    ),
    "AUTHENTICATION_BACKENDS": (list, [], setting("authentication-backends")),
    "AZURE_CLIENT_ID": (str, "", "", False, "Azure AD client ID for SSO"),
    "AZURE_CLIENT_SECRET": (str, "", "", False, "Azure AD client secret for SSO"),
    "AZURE_TENANT_ID": (str, "", "", False, "Azure AD tenant ID for SSO"),
    "SUPERUSERS": (list, [], [], False, "Emails/usernames auto-granted superuser"),
    "SOCIAL_AUTH_REDIRECT_IS_HTTPS": (bool, True, True, False, ""),
    "SOCIAL_AUTH_RAISE_EXCEPTIONS": (bool, False, False, False, ""),
    "SOCIAL_AUTH_LOGIN_URL": (str, "/login/", "/login/", False, "Social auth login URL"),
    "CACHE_URL": (
        str,
        "redis://localhost:6379/0",
        "",
        True,
        "@see https://docs.djangoproject.com/en/5.0/ref/settings/#cache-url",
    ),
    "CELERY_BROKER_URL": (
        str,
        "",
        "",
        True,
        "@see https://docs.celeryq.dev/en/stable/userguide/configuration.html",
    ),
    "CELERY_TASK_ALWAYS_EAGER": (bool, False, True, False, ""),
    "OLLAMA_BASE_URL": (
        str,
        "",
        "",
        False,
        "Base URL for Ollama API (e.g. http://localhost:11434)",
    ),
    "OLLAMA_DEFAULT_MODEL": (
        str,
        "llama3",
        "llama3",
        False,
        "Default Ollama model to use",
    ),
    "OLLAMA_TIMEOUT": (int, 120, 120, False, "Timeout in seconds for Ollama requests"),
    "HOPE_API_TOKEN": (str, "", "", True, "API token for HOPE to authenticate to AMS"),
    "HOPE_API_URL": (str, "", "", True, "Base URL for HOPE API"),
    "DATABASE_URL": (
        str,
        SmartEnv.NOTSET,
        SmartEnv.NOTSET,
        True,
        "@see https://django-environ.readthedocs.io/en/latest/types.html",
    ),
    "DEBUG": (
        bool,
        False,
        True,
        False,
        "@see https://docs.djangoproject.com/en/5.0/ref/settings/#debug",
    ),
    "SECRET_KEY": (
        str,
        SmartEnv.NOTSET,
        SmartEnv.NOTSET,
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
