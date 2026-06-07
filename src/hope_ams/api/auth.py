from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

if TYPE_CHECKING:
    from rest_framework.request import Request

from hope_ams.config import env


@dataclass
class APIUser:
    is_authenticated: bool = True
    is_active: bool = True
    is_anonymous: bool = False


class APIKeyAuthentication(BaseAuthentication):
    def authenticate(self, request: Request) -> tuple[APIUser, None] | None:
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth_header.startswith("Bearer "):
            return None
        token = auth_header.removeprefix("Bearer ")
        expected = env("AMS_API_KEY")
        if not expected:
            return None
        if token != expected:
            raise AuthenticationFailed("Invalid API key")
        return (APIUser(), None)
