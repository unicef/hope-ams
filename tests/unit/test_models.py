from __future__ import annotations

import uuid

import pytest

from hope_ams.detections.models import (
    AnomalyResult,
    BusinessArea,
    DetectionRun,
    PaymentPlan,
    Program,
    RuleConfig,
)


class TestBusinessArea:
    def test_create(self, db) -> None:
        ba = BusinessArea.objects.create(id=uuid.uuid4(), name="Test BA", slug="test-ba")
        assert str(ba) == "Test BA"

    def test_unique_id(self, db) -> None:
        uid = uuid.uuid4()
        BusinessArea.objects.create(id=uid, name="BA1", slug="ba1")
        with pytest.raises(Exception, match="unique constraint"):
            BusinessArea.objects.create(id=uid, name="BA2", slug="ba2")


class TestProgram:
    def test_create(self, db, business_area: BusinessArea) -> None:
        prog = Program.objects.create(id=uuid.uuid4(), name="Prog", business_area=business_area)
        assert str(prog) == "Prog"
        assert prog.business_area == business_area


class TestPaymentPlan:
    def test_create(self, db, program: Program, business_area: BusinessArea) -> None:
        pp = PaymentPlan.objects.create(
            id=uuid.uuid4(),
            unicef_id="PP-001",
            program=program,
            business_area=business_area,
        )
        assert str(pp) == "PP-001"
        assert pp.program == program


class TestDetectionRun:
    def test_create(self, db, payment_plan: PaymentPlan, program: Program, business_area: BusinessArea) -> None:
        run = DetectionRun.objects.create(
            phase="prevention",
            trigger="api",
            status="queued",
            payment_plan=payment_plan,
            program=program,
            business_area=business_area,
        )
        assert run.status == "queued"
        assert str(run).startswith("prevention run")
        assert run.rules_executed == 0
        assert run.anomalies_found == 0

    def test_status_choices(self, db, payment_plan: PaymentPlan, program: Program, business_area: BusinessArea) -> None:
        for status in ["queued", "running", "completed", "failed"]:
            run = DetectionRun.objects.create(
                phase="prevention",
                trigger="api",
                status=status,
                payment_plan=payment_plan,
                program=program,
                business_area=business_area,
            )
            assert run.status == status


class TestAnomalyResult:
    def test_create(self, db, payment_plan: PaymentPlan, program: Program, business_area: BusinessArea) -> None:
        run = DetectionRun.objects.create(
            phase="prevention",
            trigger="api",
            status="completed",
            payment_plan=payment_plan,
            program=program,
            business_area=business_area,
        )
        anomaly = AnomalyResult.objects.create(
            detection_run=run,
            phase="prevention",
            rule_name="unrealistic_age",
            severity="critical",
            status="open",
            title="Test anomaly",
            business_area=business_area,
            program=program,
            payment_plan=payment_plan,
            object_type="individual",
            object_id=uuid.uuid4(),
        )
        assert str(anomaly) == "[critical] Test anomaly"
        assert anomaly.status == "open"


class TestRuleConfig:
    def test_global_scope(self, db) -> None:
        rc = RuleConfig.objects.create(
            rule_name="unrealistic_age",
            enabled=True,
            config={"max_age": 120},
            scope="global",
        )
        assert str(rc) == "unrealistic_age [global]"
        assert rc.config == {"max_age": 120}
