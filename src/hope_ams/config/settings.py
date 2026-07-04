from pathlib import Path

from . import env

SETTINGS_DIR = Path(__file__).parent
PACKAGE_DIR = SETTINGS_DIR.parent
BASE_DIR = PACKAGE_DIR.parent.parent

DEBUG = env.bool("DEBUG")

DATABASES = {
    "default": env.db("DATABASE_URL"),
}

INSTALLED_APPS = [
    "hope_ams.apps.HopeAMSConfig",
    "hope_ams.web",
    "unfold.apps.DefaultAppConfig",
    "unfold.contrib.filters",
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.staticfiles",
    "django.contrib.admin",
    "rest_framework",
    "admin_extra_buttons",
    "django_celery_results",
    "social_django",
    "constance",
    "constance.backends.database",
    "flags",
    "unicef_security",
    "hope_ams.api.apps.Config",
    "hope_ams.social",
]

SITE_ID = 1

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "hope_ams.config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [PACKAGE_DIR / "web" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",
            ],
        },
    },
]

WSGI_APPLICATION = "hope_ams.config.wsgi.application"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
]

AUTHENTICATION_BACKENDS = [
    "social_core.backends.azuread_tenant.AzureADTenantOAuth2",
    "django.contrib.auth.backends.ModelBackend",
    *env.list("AUTHENTICATION_BACKENDS"),
]

AUTH_USER_MODEL = "hope_ams.AMSUser"

LANGUAGE_CODE = "en-us"
TIME_ZONE = env("TIME_ZONE")
USE_I18N = True
USE_TZ = True

STATIC_URL = env("STATIC_URL")
STATIC_ROOT = env("STATIC_ROOT")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")
SECRET_KEY = env("SECRET_KEY")

CACHES = {
    "default": env.cache("CACHE_URL"),
}

from .fragments.celery import *  # noqa: E402, F403
from .fragments.hope import *  # noqa: E402, F403
from .fragments.ollama import *  # noqa: E402, F403
from .fragments.rest_framework import *  # noqa: E402, F403
from .fragments.sentry import *  # noqa: E402, F403
from .fragments.unfold import *  # noqa: E402, F403
from .fragments.flags import *  # noqa: E402, F403
from .fragments.constance import *  # noqa: E402, F403
from .fragments.social_auth import *  # noqa: E402, F403
