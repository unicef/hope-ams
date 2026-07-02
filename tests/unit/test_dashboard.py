import pytest
from django.contrib.auth import get_user_model
from django_webtest import DjangoTestApp
from testutils.factories import AnomalyResultFactory, DetectionRunFactory, ProgrammeFactory

pytestmark = [pytest.mark.django_db]


def _auth_extra_environ() -> dict:
    return {
        "HTTP_AUTHORIZATION": "Bearer dev-ams-api-key-change-in-production",
    }


@pytest.fixture
def admin_app(db) -> DjangoTestApp:
    user = get_user_model().objects.create_superuser("admin", "admin@example.com", "password")
    app = DjangoTestApp()
    app.set_user(user)
    return app


def test_dashboard_empty(admin_app: DjangoTestApp) -> None:
    resp = admin_app.get("/api/dashboard/")
    assert resp.status_code == 200


def test_dashboard_with_data(admin_app: DjangoTestApp) -> None:
    programmes = ProgrammeFactory.create_batch(3)
    for prog in programmes:
        DetectionRunFactory.create_batch(1, programme=prog)
        AnomalyResultFactory.create_batch(5, programme=prog)
    resp = admin_app.get("/api/dashboard/")
    assert resp.status_code == 200


def test_list_all(admin_app: DjangoTestApp) -> None:
    programmes = ProgrammeFactory.create_batch(3)
    for prog in programmes:
        AnomalyResultFactory.create_batch(3, programme=prog)
    resp = admin_app.get("/api/anomalies/", extra_environ=_auth_extra_environ())
    assert resp.status_code == 200
