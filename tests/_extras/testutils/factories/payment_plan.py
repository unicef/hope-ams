import uuid

import factory

from hope_ams.models import PaymentPlan

from .base import AutoRegisterModelFactory
from .programme import ProgrammeFactory


class PaymentPlanFactory(AutoRegisterModelFactory):
    class Meta:
        model = PaymentPlan
        django_get_or_create = ("correlation_id",)

    correlation_id = factory.LazyFunction(uuid.uuid4)
    unicef_id = factory.Sequence(lambda n: f"PP-{n:04d}")
    programme = factory.SubFactory(ProgrammeFactory)
    office = factory.SelfAttribute("programme.office")
