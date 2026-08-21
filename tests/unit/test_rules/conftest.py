import uuid

import pytest


@pytest.fixture
def make_pp():
    def _factory(**overrides):
        return {
            "id": str(uuid.uuid4()),
            "unicef_id": "PP-001",
            "office": {"id": str(uuid.uuid4()), "name": "BA", "slug": "ba"},
            "programme": {"id": str(uuid.uuid4()), "name": "Prog"},
            "total_entitled_quantity": 10000.0,
            **overrides,
        }

    return _factory


@pytest.fixture
def make_payment():
    def _factory(**overrides):
        return {
            "id": uuid.uuid4(),
            "unicef_id": "PMT-001",
            "household_id": uuid.uuid4(),
            "household_unicef_id": "HH-001",
            "financial_service_provider": "FSP-A",
            "delivery_type": "cash",
            "token_number": "TOKEN-1",
            "conflicted": False,
            "excluded": False,
            "delivered_quantity": None,
            "delivery_date": None,
            "entitlement_date": None,
            "currency": "USD",
            "snapshot_data": {"individuals": []},
            **overrides,
        }

    return _factory


@pytest.fixture
def make_individual():
    def _factory(**overrides):
        return {
            "id": uuid.uuid4(),
            "unicef_id": "IND-001",
            "full_name": "Jane Doe",
            "birth_date": "1990-01-01",
            "sex": "F",
            "documents": [{"type": "national_id", "number": "12345"}],
            **overrides,
        }

    return _factory
