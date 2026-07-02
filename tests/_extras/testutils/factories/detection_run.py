import factory

from hope_ams.models import DetectionRun

from .base import AutoRegisterModelFactory
from .payment_plan import PaymentPlanFactory


class DetectionRunFactory(AutoRegisterModelFactory):
    class Meta:
        model = DetectionRun

    phase = DetectionRun.Phase.PREVENTION
    trigger = DetectionRun.Trigger.API
    status = DetectionRun.Status.QUEUED
    payment_plan = factory.SubFactory(PaymentPlanFactory)
    programme = factory.SelfAttribute("payment_plan.programme")
    office = factory.SelfAttribute("payment_plan.office")
