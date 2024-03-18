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


@pytest.fixture()
def journal_data():
    return {
        "name": "Bank Open Balance",
        "note": "Opening balalnce adjustment for Zenith Bank account",
        # "number": "JNL-000001",
        "lines": [
            {
                "account": Account.objects.get(code="3001-1").id,
                "amount": 5_000,
                "type": "credit",
            },
            {
                "account": Account.objects.get(code="1000-1").id,
                "amount": 5_000,
                "type": "debit",
            },
        ],
    }


@pytest.fixture()
def invalid_journal_data():
    return {
        "name": "Bank Open Balance",
        "note": "Opening balalnce adjustment for Zenith Bank account",
        # "number": "JNL-000001",
        "lines": [
            {
                "account": Account.objects.get(code="3001-1").id,
                "amount": 5_000,
                "type": "credit",
            },
            {
                "account": Account.objects.get(code="1000-1").id,
                "amount": 6_000,
                "type": "debit",
            },
        ],
    }
