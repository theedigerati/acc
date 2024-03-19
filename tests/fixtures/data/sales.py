import pytest
from mixer.backend.django import mixer


@pytest.fixture()
def client_data(address_data):
    return {
        "full_name": "Jane Dow",
        "business_name": "Cranks & Saw Ltd.",
        "display_name": "Cranks & Saw",
        "email": "jane@localhost",
        "phone": "+123456789",
        "shipping_address": address_data,
    }


@pytest.fixture()
def client_data_partial():
    return {
        "full_name": "Jane Dow",
        "business_name": "Cranks & Saw Ltd.",
        "display_name": "Cranks & Saw",
        "email": "jane@localhost",
        "phone": "+123456789",
    }


@pytest.fixture()
def client_object():
    """
    Client object created with mixer.
    """
    return mixer.blend("client.Client")
