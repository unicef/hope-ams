from typing import Any, cast

from constance import config
from django.conf import settings
from django.contrib.auth.models import Group


def save_to_group(user: Any = None, **kwargs: Any) -> dict[str, Any]:
    if user:
        grp = Group.objects.get(name=config.NEW_USER_DEFAULT_GROUP)
        user.groups.add(grp)
    return {}


def set_superusers(user: Any = None, is_new: bool = False, **kwargs: Any) -> dict[str, Any]:
    superusers: list[str] = cast("list[str]", getattr(settings, "SUPERUSERS", []))
    if user and is_new and user.email in superusers:
        user.is_superuser = True
        user.save()
    return {}
