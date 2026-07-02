from django.test import override_settings

from hope_ams.api.auth import APIKeyAuthentication, APIUser


def test_valid_key() -> None:
    auth = APIKeyAuthentication()
    factory = _make_request("Bearer dev-ams-api-key-change-in-production")
    user, key = auth.authenticate(factory)
    assert isinstance(user, APIUser)
    assert user.is_authenticated
    assert key is None


def test_invalid_key_raises() -> None:
    auth = APIKeyAuthentication()
    factory = _make_request("Bearer wrong-key")
    import pytest
    from rest_framework.exceptions import AuthenticationFailed

    with pytest.raises(AuthenticationFailed):
        auth.authenticate(factory)


def test_missing_header() -> None:
    auth = APIKeyAuthentication()
    factory = _make_request("")
    result = auth.authenticate(factory)
    assert result is None


@override_settings(HOPE_API_TOKEN="")
def test_empty_token_returns_none() -> None:
    auth = APIKeyAuthentication()
    factory = _make_request("Bearer dev-ams-api-key-change-in-production")
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
