import uuid
from unittest.mock import patch

import pytest
from django_webtest import DjangoTestApp

from tests.unit.conftest import pp_data


@patch("hope_ams.api.views.process_analysis.delay")
def test_submit_prevention(mock_delay, client, db) -> None:
    response = client.post_json(
        "/api/run/",
        _payload("prevention"),
    )
    assert response.status_code == 202
    data_dict = response.json
    assert data_dict["status"] == "queued"
    assert "run_id" in data_dict
    mock_delay.assert_called_once()


@patch("hope_ams.api.views.process_analysis.delay")
def test_submit_detection(mock_delay, client, db) -> None:
    response = client.post_json(
        "/api/run/",
        _payload("detection"),
    )
    assert response.status_code == 202


@pytest.fixture
def client_no_auth(db) -> DjangoTestApp:
    return DjangoTestApp()


@patch("hope_ams.api.views.process_analysis.delay")
def test_submit_unauthenticated(mock_delay, client_no_auth, db) -> None:
    response = client_no_auth.post_json(
        "/api/run/",
        _payload("prevention"),
        expect_errors=True,
    )
    assert response.status_code in (401, 403)
    mock_delay.assert_not_called()


@patch("hope_ams.api.views.process_analysis.delay")
def test_submit_invalid_branch(mock_delay, client, db) -> None:
    payload = _payload("prevention")
    payload["phase"] = "invalid"
    response = client.post_json(
        "/api/run/",
        payload,
        expect_errors=True,
    )
    assert response.status_code == 400
    mock_delay.assert_not_called()


def test_stats(client_no_auth, db) -> None:
    response = client_no_auth.get("/api/stats/", expect_errors=True)
    assert response.status_code in (401, 403)


def test_empty(client, db) -> None:
    response = client.get("/api/anomalies/")
    assert response.status_code == 200
    data_dict = response.json
    assert data_dict["count"] == 0
    assert data_dict["results"] == []


def test_with_filters(client, business_area, program, payment_plan) -> None:
    from hope_ams.models import AnomalyResult, DetectionRun

    run = DetectionRun.objects.create(
        phase="prevention",
        trigger="api",
        status="completed",
        payment_plan=payment_plan,
        programme=program,
        office=business_area,
    )
    for sev in ["low", "medium", "high", "critical"]:
        AnomalyResult.objects.create(
            detection_run=run,
            phase="prevention",
            rule_name="test_rule",
            severity=sev,
            status="open",
            title=f"Test {sev}",
            office=business_area,
            programme=program,
            payment_plan=payment_plan,
            object_type="individual",
            object_id=uuid.uuid4(),
        )
    response = client.get("/api/anomalies/?severity=high")
    assert response.status_code == 200
    data_dict = response.json
    assert data_dict["count"] == 1


def test_update_anomaly_status(client, business_area, program, payment_plan) -> None:
    from hope_ams.models import AnomalyResult, DetectionRun

    run = DetectionRun.objects.create(
        phase="prevention",
        trigger="api",
        status="completed",
        payment_plan=payment_plan,
        programme=program,
        office=business_area,
    )
    anomaly = AnomalyResult.objects.create(
        detection_run=run,
        phase="prevention",
        rule_name="test_rule",
        severity="high",
        status="open",
        title="Test anomaly",
        office=business_area,
        programme=program,
        payment_plan=payment_plan,
        object_type="individual",
        object_id=uuid.uuid4(),
    )
    response = client.patch_json(
        f"/api/anomalies/{anomaly.id}/",
        {"status": "confirmed"},
    )
    assert response.status_code == 200
    data_dict = response.json
    assert data_dict["status"] == "confirmed"


def _payload(branch: str) -> dict:
    return {
        "phase": branch,
        "callback_url": "https://hope.example.com/api/anomaly/callback/",
        "payment_plan": {
            **pp_data(),
            "payments": [
                {
                    "id": str(uuid.uuid4()),
                    "unicef_id": "PMT-001",
                    "household_id": str(uuid.uuid4()),
                    "household_unicef_id": "HH-001",
                    "status": "assigned",
                    "entitlement_quantity": 500.0,
                    "snapshot_data": {
                        "size": 4,
                        "individuals": [
                            {
                                "id": str(uuid.uuid4()),
                                "full_name": "John",
                                "birth_date": "1990-01-01",
                            },
                        ],
                    },
                },
            ],
        },
    }
