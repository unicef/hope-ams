from __future__ import annotations

from hope_ams.api.auth import APIKeyAuthentication, APIUser


class TestAuth:
    def test_valid_key(self) -> None:
        auth = APIKeyAuthentication()
        factory = _make_request("Bearer dev-ams-api-key-change-in-production")
        user, key = auth.authenticate(factory)
        assert isinstance(user, APIUser)
        assert user.is_authenticated
        assert key is None

    def test_invalid_key_raises(self) -> None:
        auth = APIKeyAuthentication()
        factory = _make_request("Bearer wrong-key")
        from rest_framework.exceptions import AuthenticationFailed
        import pytest

        with pytest.raises(AuthenticationFailed):
            auth.authenticate(factory)

    def test_missing_header(self) -> None:
        auth = APIKeyAuthentication()
        factory = _make_request("")
        result = auth.authenticate(factory)
        assert result is None


def _make_request(auth_header: str):
    from rest_framework.request import Request
    from rest_framework.test import APIRequestFactory

    factory = APIRequestFactory()
    if auth_header:
        wsgi = factory.get(
            "/api/stats/",
            HTTP_AUTHORIZATION=auth_header,
        )
    else:
        wsgi = factory.get("/api/stats/")
    return Request(wsgi)
