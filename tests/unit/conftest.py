from __future__ import annotations

import uuid

import pytest

from hope_ams.detections.models import BusinessArea, PaymentPlan, Program


UUID_BASE = uuid.uuid4()


def ba_data(**overrides: dict) -> dict:
    return {
        "id": str(UUID_BASE),
        "name": "Test BA",
        "slug": "test-ba",
        **overrides,
    }


def program_data(**overrides: dict) -> dict:
    return {
        "id": str(UUID_BASE),
        "name": "Test Program",
        **overrides,
    }


def pp_data(**overrides: dict) -> dict:
    return {
        "id": str(UUID_BASE),
        "unicef_id": "PP-001",
        "business_area": ba_data(),
        "program": program_data(),
        "status": "locked",
        "currency": "USD",
        "total_entitled_quantity": 10000.0,
        **overrides,
    }


def make_individual(**overrides: dict) -> dict:
    return {
        "id": uuid.uuid4(),
        "unicef_id": "IND-001",
        "full_name": "John Doe",
        "birth_date": "1990-01-15",
        "sex": "M",
        "relationship": "head",
        "role": "primary",
        "pregnant": False,
        "has_disability": "no",
        "documents": [],
        "phone_numbers": [],
        "wallet_name": "",
        "walner_id": "",
        **overrides,
    }


@pytest.fixture
def sample_payment() -> dict:
    return {
        "id": uuid.uuid4(),
        "unicef_id": "PMT-001",
        "household_id": uuid.uuid4(),
        "household_unicef_id": "HH-001",
        "status": "assigned",
        "entitlement_quantity": 500.0,
        "entitlement_quantity_usd": 500.0,
        "delivered_quantity": None,
        "delivered_quantity_usd": None,
        "delivery_date": None,
        "financial_service_provider": "FSP-A",
        "delivery_type": "cash",
        "currency": "USD",
        "excluded": False,
        "conflicted": False,
        "vulnerability_score": 5.0,
        "order_number": 1,
        "token_number": "",
        "snapshot_data": {
            "size": 4,
            "address": "123 Main St",
            "residence_status": "refugee",
            "primary_collector": {"name": "John", "relationship": "HEAD"},
            "individuals": [
                make_individual(
                    id=uuid.uuid4(),
                    unicef_id="IND-001",
                    full_name="Adult Head",
                    birth_date="1985-06-10",
                    sex="F",
                    relationship="head",
                    role="primary",
                    has_disability="no",
                ),
                make_individual(
                    id=uuid.uuid4(),
                    unicef_id="IND-002",
                    full_name="Child One",
                    birth_date="2015-03-20",
                    sex="M",
                    relationship="son_daughter",
                    role="child",
                    has_disability="no",
                ),
            ],
        },
    }


@pytest.fixture
def sample_payments(sample_payment: dict) -> list[dict]:
    return [sample_payment]


@pytest.fixture
def sample_submit_payload(sample_payments: list[dict]) -> dict:
    return {
        "phase": "prevention",
        "callback_url": "https://hope.example.com/api/anomaly/callback/",
        "payment_plan": {
            **pp_data(),
            "payments": sample_payments,
        },
    }


@pytest.fixture
def business_area(db) -> BusinessArea:
    return BusinessArea.objects.create(
        id=UUID_BASE,
        name="Test BA",
        slug="test-ba",
    )


@pytest.fixture
def program(db, business_area: BusinessArea) -> Program:
    return Program.objects.create(
        id=UUID_BASE,
        name="Test Program",
        business_area=business_area,
    )


@pytest.fixture
def payment_plan(db, program: Program, business_area: BusinessArea) -> PaymentPlan:
    return PaymentPlan.objects.create(
        id=UUID_BASE,
        unicef_id="PP-001",
        program=program,
        business_area=business_area,
    )
