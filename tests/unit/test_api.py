from __future__ import annotations

import uuid
from unittest.mock import patch

from tests.unit.conftest import pp_data


AUTH_HEADER = {"HTTP_AUTHORIZATION": "Bearer dev-ams-api-key-change-in-production"}


class TestSubmitRunAPI:
    @patch("hope_ams.api.views.process_analysis.delay")
    def test_submit_prevention(self, mock_delay, client, db) -> None:
        response = client.post(
            "/api/run/",
            data=_payload("prevention"),
            content_type="application/json",
            **AUTH_HEADER,
        )
        assert response.status_code == 202
        data = response.json()
        assert data["status"] == "queued"
        assert "run_id" in data
        mock_delay.assert_called_once()

    @patch("hope_ams.api.views.process_analysis.delay")
    def test_submit_detection(self, mock_delay, client, db) -> None:
        response = client.post(
            "/api/run/",
            data=_payload("detection"),
            content_type="application/json",
            **AUTH_HEADER,
        )
        assert response.status_code == 202

    @patch("hope_ams.api.views.process_analysis.delay")
    def test_submit_unauthenticated(self, mock_delay, client, db) -> None:
        response = client.post(
            "/api/run/",
            data=_payload("prevention"),
            content_type="application/json",
        )
        assert response.status_code in (401, 403)
        mock_delay.assert_not_called()

    @patch("hope_ams.api.views.process_analysis.delay")
    def test_submit_invalid_branch(self, mock_delay, client, db) -> None:
        payload = _payload("prevention")
        payload["phase"] = "invalid"
        response = client.post(
            "/api/run/",
            data=payload,
            content_type="application/json",
            **AUTH_HEADER,
        )
        assert response.status_code == 400
        mock_delay.assert_not_called()


class TestStatsAPI:
    def test_stats(self, client, db) -> None:
        response = client.get("/api/stats/", **AUTH_HEADER)
        assert response.status_code == 200
        data = response.json()
        assert "total_runs" in data
        assert "total_anomalies" in data
        assert data["total_runs"] == 0


class TestAnomalyListAPI:
    def test_empty(self, client, db) -> None:
        response = client.get("/api/anomalies/", **AUTH_HEADER)
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0
        assert data["results"] == []

    def test_with_filters(self, client, business_area, program, payment_plan) -> None:
        from hope_ams.detections.models import AnomalyResult, DetectionRun

        run = DetectionRun.objects.create(
            branch="prevention",
            trigger="api",
            status="completed",
            payment_plan=payment_plan,
            program=program,
            business_area=business_area,
        )
        for sev in ["low", "medium", "high", "critical"]:
            AnomalyResult.objects.create(
                detection_run=run,
                branch="prevention",
                rule_name="test_rule",
                severity=sev,
                status="open",
                title=f"Test {sev}",
                business_area=business_area,
                program=program,
                payment_plan=payment_plan,
                object_type="individual",
                object_id=uuid.uuid4(),
            )
        response = client.get(
            "/api/anomalies/?severity=high",
            **AUTH_HEADER,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1

    def test_update_anomaly_status(self, client, business_area, program, payment_plan) -> None:
        from hope_ams.detections.models import AnomalyResult, DetectionRun

        run = DetectionRun.objects.create(
            branch="prevention",
            trigger="api",
            status="completed",
            payment_plan=payment_plan,
            program=program,
            business_area=business_area,
        )
        anomaly = AnomalyResult.objects.create(
            detection_run=run,
            branch="prevention",
            rule_name="test_rule",
            severity="high",
            status="open",
            title="Test anomaly",
            business_area=business_area,
            program=program,
            payment_plan=payment_plan,
            object_type="individual",
            object_id=uuid.uuid4(),
        )
        response = client.patch(
            f"/api/anomalies/{anomaly.id}/",
            data={"status": "confirmed"},
            content_type="application/json",
            **AUTH_HEADER,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "confirmed"


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
                            {"id": str(uuid.uuid4()), "full_name": "John", "birth_date": "1990-01-01"},
                        ],
                    },
                },
            ],
        },
    }
