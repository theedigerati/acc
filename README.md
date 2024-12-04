## acc

This is a simple accounting REST API. Manage invoices, bills, expenses, acccounting books & reports.

- 🧾 **Invoices & Clients** - Generate detailed invoices for clients.
- 🔖 **Bills & Vendors** - Record bills received from vendors.
- 🛍 **Expenses** - Record all expenditures.
- 💸 **Payments** - Manage payments received on invoices & payments made on bills.
- 📦 **Inventory** - Simple stock tracking for items.
- 📖 **Double-Entry Accounting** - Automatic debit & credit entries for every transaction.
- 📊 **Journals & Reports** - Manage accounting books, record manual journals & generate accounting reports.
- 🏭 **Multiple Organsations** - Multi-tenancy architecture with semi-isolated approach using [PostgreSQL Schemas](https://www.postgresql.org/docs/current/ddl-schemas.html)

## Getting Started

First, clone the repo

```
git clone https://github.com/theedigerati/acc.git && cd acc
```

Next, run

```
docker compose up -d
```

The application will now be avalaible at <http://localhost:8000> and API documentation at <http://localhost:8000/docs>

For  development, run

```
docker compose up --watch
```

## Tenancy Setup

After installation a default organisation(tenant) is created automatically and Chart of Accounts set up for it.
