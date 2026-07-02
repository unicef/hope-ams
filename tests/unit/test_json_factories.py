import uuid

from testutils.factories import PaymentPayloadFactory, PlanPayloadFactory


def test_full_structure() -> None:
    """Verifica l'intera struttura del JSON prodotto da PlanPayloadFactory."""
    payload = PlanPayloadFactory()

    assert set(payload) == {
        "pk",
        "unicef_id",
        "office",
        "programme",
        "status",
        "dispersion_start_date",
        "currency",
        "total_entitled_quantity",
        "delivery_mechanism",
        "financial_service_provider",
        "reconciliation_window_in_days",
        "payments",
    }

    assert uuid.UUID(str(payload["pk"]))

    assert isinstance(payload["unicef_id"], str)
    assert payload["unicef_id"].startswith("PP-")

    ba = payload["office"]
    assert set(ba) == {"id", "name", "slug"}
    assert uuid.UUID(str(ba["id"]))
    assert isinstance(ba["name"], str)
    assert ba["name"].startswith("Office-")
    assert isinstance(ba["slug"], str)
    assert ba["slug"].startswith("office-")

    prog = payload["programme"]
    assert set(prog) == {"id", "name"}
    assert uuid.UUID(str(prog["id"]))
    assert isinstance(prog["name"], str)
    assert prog["name"].startswith("Programme-")

    assert payload["status"] == "locked"
    assert payload["dispersion_start_date"] is None
    assert payload["currency"] == "USD"
    assert payload["total_entitled_quantity"] == 10000.0
    assert payload["delivery_mechanism"] == "cash"
    assert payload["financial_service_provider"] == "FSP-A"
    assert payload["reconciliation_window_in_days"] == 30

    assert isinstance(payload["payments"], list)
    assert len(payload["payments"]) == 1


def test_payment_full_structure() -> None:
    """Verifica l'intera struttura di un payment dentro payments[]."""
    payment = PaymentPayloadFactory()

    assert set(payment) == {
        "id",
        "individual_id",
        "currency",
        "fsp",
        "delivery_type",
        "unicef_id",
        "household_unicef_id",
        "status",
        "entitlement_source",
        "vulnerability_score",
        "excluded",
        "conflicted",
        "order_number",
        "token_number",
        "current_household_data",
        "entitlement_quantity",
        "entitlement_quantity_usd",
        "delivered_quantity",
        "delivered_quantity_usd",
        "delivery_date_str",
        "snapshot",
        "errors",
    }

    assert uuid.UUID(str(payment["id"]))

    assert payment["individual_id"].startswith("IND-")
    assert payment["unicef_id"].startswith("PMT-")
    assert payment["household_unicef_id"].startswith("HH-")
    assert payment["token_number"].startswith("T-")

    assert payment["currency"] == "USD"
    assert payment["fsp"] == "FSP-A"
    assert payment["delivery_type"] == "cash"
    assert payment["status"] == "assigned"
    assert payment["entitlement_source"] == 500.0
    assert payment["vulnerability_score"] == 5.0
    assert payment["excluded"] is False
    assert payment["conflicted"] is False
    assert payment["order_number"] == 1
    assert payment["current_household_data"] == {"size": 4}
    assert payment["entitlement_quantity"] == 500.0
    assert payment["entitlement_quantity_usd"] == 500.0
    assert payment["delivered_quantity"] == 400.0
    assert payment["delivered_quantity_usd"] == 400.0
    assert payment["delivery_date_str"] == "2025-10-01"
    assert payment["snapshot"] == {"raw": True}
    assert payment["errors"] == {}


def test_passes_payment_plan_serializer_validation(db) -> None:
    from hope_ams.api.payment_plan_serializer import PaymentPlanSerializer

    payload = PlanPayloadFactory()
    serializer = PaymentPlanSerializer(data=payload)
    assert serializer.is_valid(), f"Errors: {serializer.errors}"


def test_creates_orm_objects(db) -> None:
    from hope_ams.api.payment_plan_serializer import PaymentPlanSerializer
    from hope_ams.models import Office, Payment, PaymentPlan, Programme

    payload = PlanPayloadFactory(num_payments=2)
    serializer = PaymentPlanSerializer(data=payload)
    serializer.is_valid(raise_exception=True)
    pp = serializer.save()

    assert Office.objects.count() == 1
    assert Programme.objects.count() == 1
    assert PaymentPlan.objects.count() == 1
    assert Payment.objects.count() == 2
    assert pp.payments.count() == 2


def test_override_num_payments() -> None:
    assert len(PlanPayloadFactory(num_payments=0)["payments"]) == 0
    assert len(PlanPayloadFactory(num_payments=3)["payments"]) == 3
    assert len(PlanPayloadFactory(num_payments=10)["payments"]) == 10


def test_override_top_level() -> None:
    p = PlanPayloadFactory(
        pk="11111111-2222-3333-4444-555555555555",
        currency="EUR",
        status="in_review",
        total_entitled_quantity=50000.0,
    )
    assert str(p["pk"]) == "11111111-2222-3333-4444-555555555555"
    assert p["currency"] == "EUR"
    assert p["status"] == "in_review"
    assert p["total_entitled_quantity"] == 50000.0


def test_override_office() -> None:
    p = PlanPayloadFactory(office={"id": str(uuid.uuid4()), "name": "Afghanistan", "slug": "AFG"})
    assert p["office"]["name"] == "Afghanistan"
    assert p["office"]["slug"] == "AFG"


def test_override_programme() -> None:
    p = PlanPayloadFactory(programme={"id": str(uuid.uuid4()), "name": "Winterization"})
    assert p["programme"]["name"] == "Winterization"


def test_override_payments_list() -> None:
    payments = [
        PaymentPayloadFactory(currency="EUR"),
        PaymentPayloadFactory(currency="GBP"),
    ]
    p = PlanPayloadFactory(payments=payments)
    assert len(p["payments"]) == 2
    assert p["payments"][0]["currency"] == "EUR"
    assert p["payments"][1]["currency"] == "GBP"


def test_override_single_payment_field() -> None:
    p = PlanPayloadFactory(payments=[PaymentPayloadFactory(individual_id="IND-CUSTOM")])
    assert p["payments"][0]["individual_id"] == "IND-CUSTOM"


def test_each_call_produces_unique_values() -> None:
    a = PlanPayloadFactory()
    b = PlanPayloadFactory()
    assert a["pk"] != b["pk"]
    assert a["unicef_id"] != b["unicef_id"]
    assert a["office"]["id"] != b["office"]["id"]
    assert a["payments"][0]["id"] != b["payments"][0]["id"]
