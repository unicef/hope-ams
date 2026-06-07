from pathlib import Path

from . import env
from .fragments import app
from .fragments.celery import *  # noqa: F403
from .fragments.rest_framework import *  # noqa: F403

SETTINGS_DIR = Path(__file__).parent
PACKAGE_DIR = SETTINGS_DIR.parent
BASE_DIR = PACKAGE_DIR.parent.parent

DEBUG = env.bool("DEBUG")

DATABASES = {
    "default": env.db("DATABASE_URL"),
}

INSTALLED_APPS = app.INSTALLED_APPS

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
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "hope_ams.config.wsgi.application"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
]

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

UNFOLD = {
    "SITE_TITLE": "Anomaly Management System",
    "SITE_HEADER": "AMS Admin",
    "SITE_URL": "/",
    "SITE_SYMBOL": "shield",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": False,
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": "Overview",
                "items": [
                    {
                        "title": "Dashboard",
                        "icon": "dashboard",
                        "link": "/admin/",
                    },
                ],
            },
            {
                "title": "Detection",
                "items": [
                    {
                        "title": "Detection Runs",
                        "icon": "play_arrow",
                        "link": "/admin/detections/detectionrun/",
                    },
                    {
                        "title": "Anomaly Results",
                        "icon": "warning",
                        "link": "/admin/detections/anomalyresult/",
                    },
                ],
            },
            {
                "title": "Reference Data",
                "items": [
                    {
                        "title": "Business Areas",
                        "icon": "business",
                        "link": "/admin/detections/businessarea/",
                    },
                    {
                        "title": "Programs",
                        "icon": "folder",
                        "link": "/admin/detections/program/",
                    },
                    {
                        "title": "Payment Plans",
                        "icon": "payments",
                        "link": "/admin/detections/paymentplan/",
                    },
                ],
            },
            {
                "title": "Configuration",
                "items": [
                    {
                        "title": "Rule Configurations",
                        "icon": "tune",
                        "link": "/admin/detections/ruleconfig/",
                    },
                ],
            },
        ],
    },
}
