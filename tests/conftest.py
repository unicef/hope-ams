import pytest
import responses
from django.test import override_settings
from django_webtest import DjangoTestApp

TEST_API_TOKEN = "dev-ams-api-key-change-in-production"


@pytest.fixture
def client(db) -> DjangoTestApp:
    return DjangoTestApp(
        extra_environ={
            "HTTP_AUTHORIZATION": f"Bearer {TEST_API_TOKEN}",
        }
    )


@pytest.fixture
def client_unauthenticated(db) -> DjangoTestApp:
    return DjangoTestApp()


@pytest.fixture(autouse=True)
def override_api_token():
    with override_settings(HOPE_API_TOKEN=TEST_API_TOKEN):
        yield


@pytest.fixture
def mocked_responses():
    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        yield rsps
