import pytest
from django.test.utils import override_settings

from hope_ams.detection.callback import notify_hope


HOPE_BASE = "https://hope.example.com"


@override_settings(HOPE_API_URL=HOPE_BASE)
def test_notify_hope_success(requests_mock) -> None:
    requests_mock.post(f"{HOPE_BASE}/callback/", status_code=200)
    result = notify_hope(f"{HOPE_BASE}/callback/", {"status": "completed"})
    assert result is True


@override_settings(HOPE_API_URL=HOPE_BASE)
def test_notify_hope_retry(requests_mock) -> None:
    requests_mock.post(f"{HOPE_BASE}/callback/", status_code=500)
    result = notify_hope(f"{HOPE_BASE}/callback/", {"status": "failed"})
    assert result is False


@override_settings(HOPE_API_URL=HOPE_BASE)
def test_notify_hope_ssrf_blocked(requests_mock) -> None:
    result = notify_hope("http://169.254.169.254/latest/meta-data/", {"status": "completed"})
    assert result is False


@override_settings(HOPE_API_URL="")
def test_notify_hope_no_allowed_base(requests_mock) -> None:
    result = notify_hope("https://hope.example.com/callback/", {"status": "completed"})
    assert result is False


@pytest.mark.usefixtures("requests_mock")
@override_settings(HOPE_API_URL=HOPE_BASE)
def test_notify_hope_empty_url() -> None:
    result = notify_hope("", {"status": "completed"})
    assert result is False
