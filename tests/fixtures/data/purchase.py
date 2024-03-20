import pytest
from mixer.backend.django import mixer


@pytest.fixture()
def vendor_data(address_data):
    return {
        "full_name": "Jane Dow",
        "business_name": "Cranks & Saw Ltd.",
        "display_name": "Cranks & Saw",
        "email": "jane@localhost",
        "phone": "+123456789",
        "shipping_address": address_data,
    }


@pytest.fixture()
def vendor_data_partial():
    return {
        "full_name": "Jane Dow",
        "business_name": "Cranks & Saw Ltd.",
        "display_name": "Cranks & Saw",
        "email": "jane@localhost",
        "phone": "+123456789",
    }


@pytest.fixture()
def vendor_object():
    return mixer.blend("vendor.Vendor")
