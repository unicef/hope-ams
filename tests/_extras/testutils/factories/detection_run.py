import factory

from hope_ams.models import DetectionRun
from hope_ams.models.choices import DetectionRunPhase, DetectionRunStatus, DetectionRunTrigger

from .base import AutoRegisterModelFactory
from .payment_plan import PaymentPlanFactory


class DetectionRunFactory(AutoRegisterModelFactory):
    class Meta:
        model = DetectionRun

    phase = DetectionRunPhase.PREVENTION
    trigger = DetectionRunTrigger.API
    status = DetectionRunStatus.QUEUED
    payment_plan = factory.SubFactory(PaymentPlanFactory)
    programme = factory.SelfAttribute("payment_plan.programme")
    office = factory.SelfAttribute("payment_plan.office")
