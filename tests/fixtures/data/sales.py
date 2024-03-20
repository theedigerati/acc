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


@pytest.fixture()
def invoice_object():
    invoice = mixer.blend("invoice.Invoice")
    mixer.blend("invoice.InvoiceLine", invoice=invoice, rate=1000, quantity=20)
    return invoice


@pytest.fixture()
def invoice_data(client_object, items, taxes):
    return {
        "client": client_object.id,
        "salesperson": "",
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
                "item": items[1].id,
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
def invoice_data_partial(invoice_object, client_object, items, taxes):
    return {
        "client": client_object.id,
        "salesperson": "",
        "lines": [
            {
                "id": invoice_object.lines.first().id,
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
def invoice_data_with_invalid_lines(client_object, items, taxes):
    """
    Invoice data with lines that belong to another invoice.
    """
    lines = mixer.cycle(2).blend("invoice.InvoiceLine")

    return {
        "client": client_object.id,
        "salesperson": "",
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
def payment_received_object(invoice_object):
    return mixer.blend("invoice.PaymentReceived", invoice=invoice_object)


@pytest.fixture()
def payment_received_data(invoice_object):
    return {
        "invoice": invoice_object.id,
        "amount": 5000,
        "date": "2023-05-19",
        "mode": "Bank Transfer",
    }
