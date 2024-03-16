import pytest
from apps.accounting.models import Account, AccountSubType


@pytest.fixture()
def account_data():
    return {
        "name": "Goods Inventory",
        "code": "1300-1",
        "sub_type": AccountSubType.objects.get(name="Stock").id,
        "parent": Account.objects.get(code="1300").id,
        "editable": True,
    }


@pytest.fixture()
def editable_account_object():
    return Account.objects.get(code="6002-1")


@pytest.fixture()
def non_editable_account_object():
    return Account.objects.get(code="1300")
