import uuid

import factory


class BaseDictFactory(factory.DictFactory):
    class Meta:
        abstract = True


class OfficePayloadFactory(BaseDictFactory):
    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"Office-{n}")
    slug = factory.Sequence(lambda n: f"office-{n}")


class ProgrammePayloadFactory(BaseDictFactory):
    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"Programme-{n}")


class PaymentPayloadFactory(BaseDictFactory):
    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    individual_id = factory.Sequence(lambda n: f"IND-{n:04d}")
    currency = "USD"
    fsp = "FSP-A"
    delivery_type = "cash"
    unicef_id = factory.Sequence(lambda n: f"PMT-{n:04d}")
    household_unicef_id = factory.Sequence(lambda n: f"HH-{n:04d}")
    status = "assigned"
    entitlement_source = 500.0
    vulnerability_score = 5.0
    excluded = False
    conflicted = False
    order_number = 1
    token_number = factory.Sequence(lambda n: f"T-{n:04d}")
    current_household_data = {"size": 4}
    entitlement_quantity = 500.0
    entitlement_quantity_usd = 500.0
    delivered_quantity = 400.0
    delivered_quantity_usd = 400.0
    delivery_date_str = "2025-10-01"
    snapshot = {"raw": True}
    errors = {}


class PlanPayloadFactory(BaseDictFactory):
    class Params:
        num_payments = 1

    pk = factory.LazyFunction(lambda: str(uuid.uuid4()))
    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    unicef_id = factory.Sequence(lambda n: f"PP-{n:04d}")
    office = factory.SubFactory(OfficePayloadFactory)
    programme = factory.SubFactory(ProgrammePayloadFactory)
    status = "locked"
    dispersion_start_date = None
    currency = "USD"
    total_entitled_quantity = 10000.0
    delivery_mechanism = "cash"
    financial_service_provider = "FSP-A"
    reconciliation_window_in_days = 30
    payments = factory.LazyAttribute(lambda o: [PaymentPayloadFactory() for _ in range(o.num_payments)])


class RunPayloadFactory(BaseDictFactory):
    class Params:
        num_payments = 1

    phase = "prevention"
    callback_url = "https://hope.example.com/api/anomaly/callback/"
    payment_plan = factory.LazyAttribute(
        lambda o: {
            k: v for k, v in PlanPayloadFactory(num_payments=o.num_payments).items() if k != "dispersion_start_date"
        }
    )
