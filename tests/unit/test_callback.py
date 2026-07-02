from hope_ams.detection.callback import notify_hope


def test_notify_hope_success(requests_mock) -> None:
    requests_mock.post("https://hope.example.com/callback/", status_code=200)
    result = notify_hope("https://hope.example.com/callback/", {"status": "completed"})
    assert result is True


def test_notify_hope_retry(requests_mock) -> None:
    requests_mock.post("https://hope.example.com/callback/", status_code=500)
    result = notify_hope("https://hope.example.com/callback/", {"status": "failed"})
    assert result is False
