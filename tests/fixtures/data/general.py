import pytest
from mixer.backend.django import mixer


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


@pytest.fixture()
def address_data():
    return {
        "line1": "2 Brown Str.,",
        "line2": "Opp. New Road",
        "city": "city",
        "state": "state",
        "postcode": "94105",
        "country": "country",
    }


@pytest.fixture()
def address_object():
    """
    Address object created with mixer.
    """
    return mixer.blend("address.Address")


@pytest.fixture()
def items():
    return mixer.cycle(3).blend(
        "item.Item", type="goods", selling_price=100, cost_price=50
    )


@pytest.fixture()
def taxes():
    return mixer.cycle(2).blend("tax.Tax", rate=2.5)
