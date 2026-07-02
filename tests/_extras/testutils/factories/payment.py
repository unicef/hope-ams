import uuid

import factory

from hope_ams.models import Payment

from .base import AutoRegisterModelFactory
from .payment_plan import PaymentPlanFactory


class PaymentFactory(AutoRegisterModelFactory):
    class Meta:
        model = Payment
        django_get_or_create = ("correlation_id",)

    correlation_id = factory.LazyFunction(uuid.uuid4)
    plan = factory.SubFactory(PaymentPlanFactory)
    individual_id = factory.Sequence(lambda n: f"IND-{n:04d}")
    currency = "USD"
    fsp = "FSP-A"
    delivery_type = "cash"
    unicef_id = factory.Sequence(lambda n: f"PMT-{n:04d}")
    status = "assigned"
