#!/bin/sh

echo "Building the project..."
# pip install -r requirements.txt
pip install --upgrade pip pip-tools
pip-sync requirements.txt requirements_dev.txt

echo "Collect Static..."
python manage.py collectstatic --no-input

echo "Make Migration..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "Setup tenancy..."
python manage.py setup_tenancy

echo "Starting server..."
python manage.py runserver 0.0.0.0:8000
