import pytest
from mixer.backend.django import mixer


# ===== TAX APP =====
@pytest.fixture()
def tax_data():
    return {"name": "VAT", "rate": 5.5}


@pytest.fixture()
def tax_object():
    return mixer.blend("tax.Tax", name="Consumption")


@pytest.fixture()
def tax_bulk_data():
    tax = mixer.blend("tax.Tax", name="Consumption")

    return [
        {"name": "VAT", "rate": 5.5},
        {"name": "Sales Tax", "rate": 7},
        {"id": tax.id, "name": "Consumptions", "rate": 8},
    ]
