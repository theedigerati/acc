import pytest
from mixer.backend.django import mixer


@pytest.fixture()
def item_data():
    return {
        "type": "goods",
        "name": "Polystar Air Conditioner",
        "sellable": True,
        "track_stock": True,
        "selling_price": 100,
        "cost_price": 50,
    }


@pytest.fixture()
def item_data_partial():
    return {
        "stock_on_hand": 50,
        "low_stock_threshold": 20,
    }


@pytest.fixture()
def item_object():
    return mixer.blend("item.Item", type="goods", selling_price=100, cost_price=50)
