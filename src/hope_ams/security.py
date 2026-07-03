from typing import TYPE_CHECKING, Any

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

if TYPE_CHECKING:
    from django.http import HttpRequest


_LOCAL_IPS = frozenset({"127.0.0.1", "::1", "localhost"})


class AnyUserAuthBackend(ModelBackend):
    """DEBUG-only auth backend that auto-creates users on login.

    Only activates when the request originates from localhost.
    """

    def authenticate(
        self,
        request: HttpRequest | None,
        username: str | None = None,
        password: str | None = None,
        **kwargs: Any,
    ) -> Any:
        if not settings.DEBUG:
            return None
        if not request:
            return None
        remote_addr = request.META.get("REMOTE_ADDR", "")
        if remote_addr not in _LOCAL_IPS:
            return None
        if username in {"admin", "superuser", "administrator", "sax"}:
            user, _ = get_user_model().objects.update_or_create(
                username=username,
                defaults={"is_staff": True, "is_active": True, "is_superuser": True},
            )
            return user
        if username == "staff":
            user, _ = get_user_model().objects.update_or_create(
                username=username,
                defaults={"is_staff": True, "is_active": True, "is_superuser": False},
            )
            return user
        return None
