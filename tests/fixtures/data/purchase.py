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


@pytest.fixture()
def bill_object():
    bill = mixer.blend("bill.Bill")
    mixer.blend("bill.BillLine", bill=bill, rate=1000, quantity=20)
    return bill


@pytest.fixture()
def bill_data(vendor_object, items, taxes):
    return {
        "vendor": vendor_object.id,
        "lines": [
            {
                "item": items[0].id,
                "description": "rando",
                "quantity": 20,
                "rate": 15_000,
                "taxes": [tax.id for tax in taxes],
                "order": 0,
            },
            {
                "id": 0,
                "name": "A new product",
                "description": "rando",
                "quantity": 20,
                "rate": 15_000,
                "taxes": [],
                "order": 1,
            },
            {
                "id": 0,
                "item": items[2].id,
                "description": "rando",
                "quantity": 20,
                "rate": 15_000,
                "taxes": [],
                "order": 2,
            },
        ],
    }


@pytest.fixture()
def bill_data_partial(bill_object, vendor_object, items, taxes):
    return {
        "vendor": vendor_object.id,
        "lines": [
            {
                "id": bill_object.lines.first().id,
                "item": items[0].id,
                "description": "rando",
                "quantity": 20,
                "rate": 15_000,
                "taxes": [tax.id for tax in taxes],
                "order": 0,
            },
            {
                "id": 0,
                "item": items[1].id,
                "description": "rando",
                "quantity": 20,
                "rate": 15_000,
                "taxes": [tax.id for tax in taxes],
                "order": 1,
            },
        ],
    }


@pytest.fixture()
def bill_data_with_invalid_lines(vendor_object, items, taxes):
    """
    Bill data with lines that belong to another bill.
    """
    lines = mixer.cycle(2).blend("bill.BillLine")

    return {
        "vendor": vendor_object.id,
        "lines": [
            {
                "id": lines[0].id,
                "item": items[0].id,
                "description": "rando",
                "quantity": 20,
                "rate": 15_000,
                "taxes": [tax.id for tax in taxes],
                "order": 0,
            },
            {
                "id": lines[1].id,
                "item": items[1].id,
                "description": "rando",
                "quantity": 20,
                "rate": 15_000,
                "taxes": [],
                "order": 1,
            },
        ],
    }


@pytest.fixture()
def payment_made_object(bill_object):
    return mixer.blend("bill.PaymentMade", bill=bill_object)


@pytest.fixture()
def payment_made_data(bill_object):
    return {
        "bill": bill_object.id,
        "amount": 5000,
        "date": "2023-05-19",
        "mode": "Bank Transfer",
    }


@pytest.fixture()
def expense_object():
    return mixer.blend("expense.Expense")


@pytest.fixture()
def expense_data(vendor_object, taxes):
    return {
        "vendor": vendor_object.id,
        "account": 1,
        "amount": 20_000,
        "taxes": [tax.id for tax in taxes],
        "paid_through": 2,
    }
