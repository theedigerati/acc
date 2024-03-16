pip-install-dev:
	pip install --upgrade pip pip-tools
	pip-sync requirements.txt requirements_dev.txt
  
pip-install:
	pip install --upgrade pip pip-tools
	pip-sync requirements.txt
  
pip-update:
	pip install --upgrade pip pip-tools
	pip-compile requirements.in
	pip-compile requirements_dev.in
	pip-sync requirements.txt requirements_dev.txt

lint:
	ruff check .

lint-fix:
	ruff check . --fix

checkmigrations:
	python manage.py makemigrations --check --no-input --dry-run

migrations:
	python manage.py makemigrations

migrate:
	python manage.py makemigrations && python manage.py migrate

server:
	python manage.py runserver

shell :
	python manage.py shell
