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


@patch("hope_ams.api.views.process_analysis.delay")
def test_submit_missing_phase(mock_delay, client, db) -> None:
    payload = _payload("prevention")
    del payload["phase"]
    response = client.post_json(
        "/api/run/",
        payload,
        expect_errors=True,
    )
    assert response.status_code == 400
    mock_delay.assert_not_called()


@patch("hope_ams.api.views.process_analysis.delay")
def test_submit_missing_payments(mock_delay, client, db) -> None:
    payload = _payload("prevention")
    del payload["payment_plan"]["payments"]
    response = client.post_json(
        "/api/run/",
        payload,
        expect_errors=True,
    )
    assert response.status_code == 400
    mock_delay.assert_not_called()


def test_submit_check(client, db) -> None:
    response = client.post_json(
        "/api/check/",
        _check_payload(),
    )
    assert response.status_code == 201
    data_dict = response.json
    assert "correlation_id" in data_dict
    assert "id" in data_dict


def test_submit_check_unauthenticated(client_no_auth, db) -> None:
    response = client_no_auth.post_json(
        "/api/check/",
        _check_payload(),
        expect_errors=True,
    )
    assert response.status_code in (401, 403)


def test_stats_unauthenticated(client_no_auth, db) -> None:
    response = client_no_auth.get("/api/stats/", expect_errors=True)
    assert response.status_code in (401, 403)


def test_stats_with_auth(client, db) -> None:
    response = client.get("/api/stats/")
    assert response.status_code == 200
    data_dict = response.json
    assert "total_runs" in data_dict
    assert "total_anomalies" in data_dict
    assert "by_severity" in data_dict
    assert "by_phase" in data_dict


def test_empty(client, db) -> None:
    response = client.get("/api/anomalies/")
    assert response.status_code == 200
    data_dict = response.json
    assert data_dict["count"] == 0
    assert data_dict["results"] == []


def test_run_detail(client, business_area, program, payment_plan) -> None:
    from hope_ams.models import DetectionRun

    run = DetectionRun.objects.create(
        phase="prevention",
        trigger="api",
        status="completed",
        payment_plan=payment_plan,
        programme=program,
        office=business_area,
    )
    response = client.get(f"/api/runs/{run.id}/")
    assert response.status_code == 200
    data_dict = response.json
    assert data_dict["id"] == run.id
    assert data_dict["phase"] == "prevention"
    assert data_dict["status"] == "completed"


def test_run_detail_not_found(client, db) -> None:
    response = client.get("/api/runs/999/", expect_errors=True)
    assert response.status_code == 404
    assert response.json["error"] == "Run not found"


def test_run_detail_unauthenticated(client_no_auth, db) -> None:
    response = client_no_auth.get("/api/runs/1/", expect_errors=True)
    assert response.status_code in (401, 403)


def test_stats_with_data(client, business_area, program, payment_plan) -> None:
    from hope_ams.models import AnomalyResult, DetectionRun

    run = DetectionRun.objects.create(
        phase="prevention",
        trigger="api",
        status="completed",
        payment_plan=payment_plan,
        programme=program,
        office=business_area,
    )
    AnomalyResult.objects.create(
        detection_run=run,
        phase="prevention",
        rule_name="test_rule",
        severity="low",
        status="open",
        title="Test anomaly",
        office=business_area,
        programme=program,
        payment_plan=payment_plan,
        object_type="individual",
        object_id=uuid.uuid4(),
    )
    response = client.get("/api/stats/")
    assert response.status_code == 200
    data_dict = response.json
    assert data_dict["total_runs"] == 1
    assert data_dict["total_anomalies"] == 1
    assert data_dict["by_severity"]["low"] == 1
    assert data_dict["by_phase"]["prevention"] == 1


def test_anomaly_list_status_filter(client, business_area, program, payment_plan) -> None:
    from hope_ams.models import AnomalyResult, DetectionRun

    run = DetectionRun.objects.create(
        phase="prevention",
        trigger="api",
        status="completed",
        payment_plan=payment_plan,
        programme=program,
        office=business_area,
    )
    AnomalyResult.objects.create(
        detection_run=run,
        phase="prevention",
        rule_name="test_rule",
        severity="low",
        status="open",
        title="Open anomaly",
        office=business_area,
        programme=program,
        payment_plan=payment_plan,
        object_type="individual",
        object_id=uuid.uuid4(),
    )
    AnomalyResult.objects.create(
        detection_run=run,
        phase="prevention",
        rule_name="test_rule",
        severity="high",
        status="confirmed",
        title="Confirmed anomaly",
        office=business_area,
        programme=program,
        payment_plan=payment_plan,
        object_type="individual",
        object_id=uuid.uuid4(),
    )
    response = client.get("/api/anomalies/?status=open")
    assert response.status_code == 200
    data_dict = response.json
    assert data_dict["count"] == 1


def test_anomaly_list_phase_filter(client, business_area, program, payment_plan) -> None:
    from hope_ams.models import AnomalyResult, DetectionRun

    run = DetectionRun.objects.create(
        phase="detection",
        trigger="api",
        status="completed",
        payment_plan=payment_plan,
        programme=program,
        office=business_area,
    )
    AnomalyResult.objects.create(
        detection_run=run,
        phase="detection",
        rule_name="test_rule",
        severity="low",
        status="open",
        title="Detection anomaly",
        office=business_area,
        programme=program,
        payment_plan=payment_plan,
        object_type="individual",
        object_id=uuid.uuid4(),
    )
    response = client.get("/api/anomalies/?phase=detection")
    assert response.status_code == 200
    data_dict = response.json
    assert data_dict["count"] == 1
    assert data_dict["results"][0]["phase"] == "detection"


def test_anomaly_list_unauthenticated(client_no_auth, db) -> None:
    response = client_no_auth.get("/api/anomalies/", expect_errors=True)
    assert response.status_code in (401, 403)


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


def test_with_multiple_filters(client, business_area, program, payment_plan) -> None:
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
    office_id = str(business_area.correlation_id)
    response = client.get(f"/api/anomalies/?office_id={office_id}&phase=prevention")
    assert response.status_code == 200
    data_dict = response.json
    assert data_dict["count"] == 4


def test_run_filter(client, business_area, program, payment_plan) -> None:
    from hope_ams.models import AnomalyResult, DetectionRun

    run = DetectionRun.objects.create(
        phase="prevention",
        trigger="api",
        status="completed",
        payment_plan=payment_plan,
        programme=program,
        office=business_area,
    )
    AnomalyResult.objects.create(
        detection_run=run,
        phase="prevention",
        rule_name="test_rule",
        severity="low",
        status="open",
        title="Test anomaly",
        office=business_area,
        programme=program,
        payment_plan=payment_plan,
        object_type="individual",
        object_id=uuid.uuid4(),
    )
    response = client.get(f"/api/anomalies/?run_id={run.id}")
    assert response.status_code == 200
    data_dict = response.json
    assert data_dict["count"] == 1


def test_rule_name_filter(client, business_area, program, payment_plan) -> None:
    from hope_ams.models import AnomalyResult, DetectionRun

    run = DetectionRun.objects.create(
        phase="prevention",
        trigger="api",
        status="completed",
        payment_plan=payment_plan,
        programme=program,
        office=business_area,
    )
    AnomalyResult.objects.create(
        detection_run=run,
        phase="prevention",
        rule_name="rule_a",
        severity="low",
        status="open",
        title="Test A",
        office=business_area,
        programme=program,
        payment_plan=payment_plan,
        object_type="individual",
        object_id=uuid.uuid4(),
    )
    AnomalyResult.objects.create(
        detection_run=run,
        phase="prevention",
        rule_name="rule_b",
        severity="low",
        status="open",
        title="Test B",
        office=business_area,
        programme=program,
        payment_plan=payment_plan,
        object_type="individual",
        object_id=uuid.uuid4(),
    )
    response = client.get("/api/anomalies/?rule_name=rule_a")
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


def test_update_anomaly_invalid_status(client, business_area, program, payment_plan) -> None:
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
        {"status": "non_existent"},
        expect_errors=True,
    )
    assert response.status_code == 400


def test_update_anomaly_not_found(client, db) -> None:
    response = client.patch_json(
        "/api/anomalies/999/",
        {"status": "confirmed"},
        expect_errors=True,
    )
    assert response.status_code == 404
    assert response.json["error"] == "Anomaly not found"


def test_update_anomaly_unauthenticated(client_no_auth, business_area, program, payment_plan) -> None:
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
    response = client_no_auth.patch_json(
        f"/api/anomalies/{anomaly.id}/",
        {"status": "confirmed"},
        expect_errors=True,
    )
    assert response.status_code in (401, 403)


def test_pagination(client, business_area, program, payment_plan) -> None:
    from hope_ams.models import AnomalyResult, DetectionRun

    run = DetectionRun.objects.create(
        phase="prevention",
        trigger="api",
        status="completed",
        payment_plan=payment_plan,
        programme=program,
        office=business_area,
    )
    for i in range(5):
        AnomalyResult.objects.create(
            detection_run=run,
            phase="prevention",
            rule_name="test_rule",
            severity="low",
            status="open",
            title=f"Test {i}",
            office=business_area,
            programme=program,
            payment_plan=payment_plan,
            object_type="individual",
            object_id=uuid.uuid4(),
        )
    response = client.get("/api/anomalies/?page=1&page_size=2")
    assert response.status_code == 200
    data_dict = response.json
    assert data_dict["count"] == 5
    assert len(data_dict["results"]) == 2


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


def _check_payload() -> dict:
    d = pp_data()
    return {
        "office": d["office"],
        "programme": d["programme"],
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
    }
