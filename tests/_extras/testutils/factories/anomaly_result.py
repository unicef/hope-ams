import uuid

import factory

from hope_ams.models import AnomalyResult

from .base import AutoRegisterModelFactory
from .detection_run import DetectionRunFactory


class AnomalyResultFactory(AutoRegisterModelFactory):
    class Meta:
        model = AnomalyResult

    detection_run = factory.SubFactory(DetectionRunFactory)
    phase = factory.SelfAttribute("detection_run.phase")
    rule_name = "test_rule"
    severity = AnomalyResult.Severity.MEDIUM
    status = AnomalyResult.Status.OPEN
    title = factory.Sequence(lambda n: f"Anomaly {n}")
    description = ""
    office = factory.SelfAttribute("detection_run.office")
    programme = factory.SelfAttribute("detection_run.programme")
    payment_plan = factory.SelfAttribute("detection_run.payment_plan")
    object_type = "individual"
    object_id = factory.LazyFunction(uuid.uuid4)
    object_unicef_id = ""
