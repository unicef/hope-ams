import uuid

import pytest
from django_webtest import DjangoTestApp

from hope_ams.models import Office, Payment, PaymentPlan, Programme


@pytest.fixture
def client_ams(db) -> DjangoTestApp:
    return DjangoTestApp(
        extra_environ={
            "HTTP_AUTHORIZATION": "Bearer dev-ams-api-key-change-in-production",
        }
    )


def _check_payload() -> dict:
    return {
        "pk": str(uuid.uuid4()),
        "office": {
            "id": str(uuid.uuid4()),
            "name": "Afghanistan",
            "slug": "AFG",
        },
        "programme": {
            "id": str(uuid.uuid4()),
            "name": "Winterization",
        },
        "status": "locked",
        "currency": "USD",
        "total_entitled_quantity": 10000.0,
        "delivery_mechanism": "cash",
        "financial_service_provider": "FSP-A",
        "reconciliation_window_in_days": 30,
        "payments": [
            {
                "id": str(uuid.uuid4()),
                "individual_id": "IND-001",
                "currency": "USD",
                "fsp": "FSP-A",
                "delivery_type": "cash",
                "unicef_id": "PMT-001",
                "household_unicef_id": "HH-001",
                "status": "assigned",
                "entitlement_source": 500.0,
                "vulnerability_score": 5.0,
                "excluded": False,
                "conflicted": False,
                "order_number": 1,
                "token_number": "T-001",
                "current_household_data": {"size": 4},
                "entitlement_quantity": 500.0,
                "entitlement_quantity_usd": 500.0,
                "delivered_quantity": 400.0,
                "delivered_quantity_usd": 400.0,
                "delivery_date_str": "2025-10-01",
                "snapshot": {"raw": True},
                "errors": {},
            }
        ],
    }


def test_valid_payload_serializes(db) -> None:
    from hope_ams.api.payment_plan_serializer import PaymentPlanSerializer

    payload = _check_payload()
    serializer = PaymentPlanSerializer(data=payload)
    assert serializer.is_valid(), f"Validation errors: {serializer.errors}"


def test_creates_office(db) -> None:
    from hope_ams.api.payment_plan_serializer import PaymentPlanSerializer

    office_id = uuid.uuid4()
    payload = _check_payload()
    payload["office"]["id"] = str(office_id)

    serializer = PaymentPlanSerializer(data=payload)
    serializer.is_valid(raise_exception=True)
    serializer.save()

    assert Office.objects.get(correlation_id=office_id).name == "Afghanistan"


def test_creates_programme(db) -> None:
    from hope_ams.api.payment_plan_serializer import PaymentPlanSerializer

    prog_id = uuid.uuid4()
    payload = _check_payload()
    payload["programme"]["id"] = str(prog_id)

    serializer = PaymentPlanSerializer(data=payload)
    serializer.is_valid(raise_exception=True)
    serializer.save()

    assert Programme.objects.get(correlation_id=prog_id).name == "Winterization"


def test_creates_payment_plan(db) -> None:
    from hope_ams.api.payment_plan_serializer import PaymentPlanSerializer

    pp_correlation = uuid.uuid4()
    payload = _check_payload()
    payload["pk"] = str(pp_correlation)

    serializer = PaymentPlanSerializer(data=payload)
    serializer.is_valid(raise_exception=True)
    payment_plan = serializer.save()

    assert payment_plan.correlation_id == pp_correlation
    assert payment_plan.unicef_id == ""
    assert payment_plan.status == "locked"
    assert payment_plan.currency == "USD"
    assert payment_plan.total_entitled_quantity is not None


def test_creates_payment_records(db) -> None:
    from hope_ams.api.payment_plan_serializer import PaymentPlanSerializer

    payload = _check_payload()
    payment_id = uuid.UUID(payload["payments"][0]["id"])

    serializer = PaymentPlanSerializer(data=payload)
    serializer.is_valid(raise_exception=True)
    payment_plan = serializer.save()

    assert Payment.objects.filter(plan=payment_plan).count() == 1
    payment_record = Payment.objects.get(correlation_id=payment_id)
    assert payment_record.individual_id == "IND-001"
    assert payment_record.currency == "USD"
    assert payment_record.unicef_id == "PMT-001"
    assert payment_record.household_unicef_id == "HH-001"
    assert payment_record.entitlement_source is not None


def test_upserts_existing_payment(db) -> None:
    from hope_ams.api.payment_plan_serializer import PaymentPlanSerializer

    existing_ba = Office.objects.create(correlation_id=uuid.uuid4(), name="Old BA", slug="old-ba")
    existing_prog = Programme.objects.create(correlation_id=uuid.uuid4(), name="Old Prog", office=existing_ba)
    existing_pp, _ = PaymentPlan.objects.update_or_create(
        correlation_id=uuid.uuid4(),
        defaults={"programme": existing_prog, "office": existing_ba},
    )

    payment_id = uuid.uuid4()
    Payment.objects.create(
        plan=existing_pp,
        correlation_id=payment_id,
        individual_id="IND-OLD",
        currency="USD",
        fsp="FSP-B",
        delivery_type="mobile_money",
    )

    payload = _check_payload()
    payload["pk"] = str(existing_pp.correlation_id)
    payload["office"]["id"] = str(existing_ba.correlation_id)
    payload["programme"]["id"] = str(existing_prog.correlation_id)
    payload["payments"][0]["id"] = str(payment_id)

    serializer = PaymentPlanSerializer(data=payload)
    serializer.is_valid(raise_exception=True)
    serializer.save()

    updated = Payment.objects.get(correlation_id=payment_id)
    assert updated.individual_id == "IND-001"
    assert updated.delivery_type == "cash"
    assert Payment.objects.filter(plan=existing_pp).count() == 1


def test_pk_field_maps_to_correlation_id(db) -> None:
    from hope_ams.api.payment_plan_serializer import PaymentPlanSerializer

    pp_correlation = uuid.uuid4()
    payload = _check_payload()
    payload["pk"] = str(pp_correlation)

    serializer = PaymentPlanSerializer(data=payload)
    serializer.is_valid(raise_exception=True)
    result = serializer.save()

    assert result.correlation_id == pp_correlation


def test_serializes_all_fields(db) -> None:
    from hope_ams.api.payment_plan_serializer import PaymentPlanPaymentSerializer

    ba = Office.objects.create(correlation_id=uuid.uuid4(), name="BA1", slug="ba1")
    prog = Programme.objects.create(correlation_id=uuid.uuid4(), name="P1", office=ba)
    PaymentPlan.objects.create(correlation_id=uuid.uuid4(), programme=prog, office=ba)

    payload = {
        "id": str(uuid.uuid4()),
        "individual_id": "IND-002",
        "currency": "EUR",
        "fsp": "FSP-X",
        "delivery_type": "bank_transfer",
        "unicef_id": "PMT-002",
        "household_unicef_id": "HH-002",
        "status": "paid",
        "entitlement_source": 1000.0,
        "vulnerability_score": 8.5,
        "excluded": True,
        "conflicted": True,
        "order_number": 2,
        "token_number": "T-002",
        "current_household_data": {"size": 6},
        "entitlement_quantity": 1000.0,
        "entitlement_quantity_usd": 1100.0,
        "delivered_quantity": 900.0,
        "delivered_quantity_usd": 990.0,
        "delivery_date_str": "2025-11-15",
        "snapshot": {"check": True},
        "errors": {"note": "ok"},
    }

    serializer = PaymentPlanPaymentSerializer(data=payload)
    assert serializer.is_valid(), f"Errors: {serializer.errors}"
    validated = serializer.validated_data
    assert validated["individual_id"] == "IND-002"
    assert validated["currency"] == "EUR"
    assert validated["delivery_type"] == "bank_transfer"
    assert validated["unicef_id"] == "PMT-002"
    assert validated["status"] == "paid"
    assert validated["excluded"] is True
    assert validated["conflicted"] is True
    assert validated["entitlement_quantity"] is not None


def test_accepts_valid_payload(client, db) -> None:
    response = client.post_json(
        "/api/check/",
        _check_payload(),
    )
    assert response.status_code == 201


def test_returns_payment_plan_id(client, db) -> None:
    pp_correlation = str(uuid.uuid4())
    payload = _check_payload()
    payload["pk"] = pp_correlation

    response = client.post_json(
        "/api/check/",
        payload,
    )
    assert response.status_code == 201
    data = response.json
    assert str(data["correlation_id"]) == pp_correlation


def test_returns_payments_count(client, db) -> None:
    response = client.post_json(
        "/api/check/",
        _check_payload(),
    )
    assert response.json["payments_count"] == 1


def test_unauthenticated_returns_401(client_unauthenticated, db) -> None:
    response = client_unauthenticated.post_json(
        "/api/check/",
        _check_payload(),
        expect_errors=True,
    )
    assert response.status_code in (401, 403)


def test_invokes_db_creations(client, db) -> None:
    initial_ba_count = Office.objects.count()
    initial_prog_count = Programme.objects.count()
    initial_pp_count = PaymentPlan.objects.count()
    initial_payment_count = Payment.objects.count()

    response = client.post_json(
        "/api/check/",
        _check_payload(),
    )
    assert response.status_code == 201

    assert Office.objects.count() == initial_ba_count + 1
    assert Programme.objects.count() == initial_prog_count + 1
    assert PaymentPlan.objects.count() == initial_pp_count + 1
    assert Payment.objects.count() == initial_payment_count + 1


def test_multiple_payments_persisted(db) -> None:
    payload = _check_payload()
    extra_payment = {
        "id": str(uuid.uuid4()),
        "individual_id": "IND-002",
        "currency": "EUR",
        "fsp": "FSP-B",
        "delivery_type": "mobile_money",
        "unicef_id": "PMT-002",
    }
    payload["payments"].append(extra_payment)

    from hope_ams.api.payment_plan_serializer import PaymentPlanSerializer

    serializer = PaymentPlanSerializer(data=payload)
    serializer.is_valid(raise_exception=True)
    result = serializer.save()

    assert result.payments.count() == 2


@pytest.mark.django_db
def test_update_existing_office(client, db) -> None:
    existing_ba = Office.objects.create(correlation_id=uuid.uuid4(), name="Old Name", slug="old-slug")

    payload = _check_payload()
    payload["office"]["id"] = str(existing_ba.correlation_id)

    response = client.post_json(
        "/api/check/",
        payload,
    )
    assert response.status_code == 201
    updated_ba = Office.objects.get(pk=existing_ba.pk)
    assert updated_ba.name == "Afghanistan"


@pytest.mark.django_db
def test_new_fields_exist_on_payment_model() -> None:
    from hope_ams.models import Payment

    fields = [f.name for f in Payment._meta.get_fields()]
    assert "unicef_id" in fields
    assert "household_id" in fields
    assert "household_unicef_id" in fields
    assert "status" in fields
    assert "entitlement_source" in fields
    assert "vulnerability_score" in fields
    assert "excluded" in fields
    assert "conflicted" in fields
    assert "order_number" in fields
    assert "token_number" in fields
    assert "current_household_data" in fields
    assert "correlation_id" in fields


def test_str_uses_unicef_id(db) -> None:
    pp_correlation = uuid.uuid4()
    ba = Office.objects.create(correlation_id=uuid.uuid4(), name="BA1", slug="ba1")
    prog = Programme.objects.create(correlation_id=uuid.uuid4(), name="P1", office=ba)
    pp = PaymentPlan.objects.create(correlation_id=pp_correlation, programme=prog, office=ba)
    p = Payment.objects.create(
        plan=pp,
        correlation_id=uuid.uuid4(),
        individual_id="I1",
        currency="USD",
        fsp="FSP",
        delivery_type="cash",
        unicef_id="PMT-UUID",
    )
    assert str(p) == "PMT-UUID"


def test_new_fields_exist_on_payment_plan_model(db) -> None:
    from hope_ams.models import PaymentPlan

    fields = [f.name for f in PaymentPlan._meta.get_fields()]
    assert "status" in fields
    assert "dispersion_start_date" in fields
    assert "currency" in fields
    assert "total_entitled_quantity" in fields
    assert "delivery_mechanism" in fields
    assert "financial_service_provider" in fields
    assert "reconciliation_window_in_days" in fields


def test_payment_plan_defaults(db) -> None:
    ba = Office.objects.create(correlation_id=uuid.uuid4(), name="BA1", slug="ba1")
    prog = Programme.objects.create(correlation_id=uuid.uuid4(), name="P1", office=ba)
    pp = PaymentPlan.objects.create(correlation_id=uuid.uuid4(), programme=prog, office=ba)
    assert pp.status == ""
    assert pp.currency == "USD"


def test_delivery_date_str_parses_correctly(db) -> None:
    from hope_ams.api.payment_plan_serializer import PaymentPlanPaymentSerializer

    payload = {
        "id": str(uuid.uuid4()),
        "individual_id": "IND-001",
        "currency": "USD",
        "fsp": "FSP",
        "delivery_type": "cash",
        "status": "paid",
        "entitlement_quantity": 500.0,
        "delivered_quantity": 400.0,
        "delivery_date_str": "2025-03-15",
    }

    serializer = PaymentPlanPaymentSerializer(data=payload)
    assert serializer.is_valid(), f"Errors: {serializer.errors}"
    validated_date = serializer.validated_data.get("delivery_date")
    assert validated_date is not None
    assert str(validated_date)[:10] == "2025-03-15"
