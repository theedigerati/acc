#!/bin/sh

# Exit on error
set -o errexit

echo "Running Migrations..."
poetry run python manage.py migrate --noinput

echo "Setup tenancy..."
poetry run python manage.py setup_tenancy
