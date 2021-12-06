copy-termux-shortcuts:
	@rm -r $(HOME)/.shortcuts/*
	@cp -a ./scripts/termux/. $(HOME)/.shortcuts/

test:
	@export APP_ENV=TEST && cd mono && pipenv run python manage.py test --parallel 12 --failfast

cov:
	@export APP_ENV=TEST && cd mono && pipenv run coverage run --source='.' manage.py test -b --timing \
		&& pipenv run coverage html \
		&& firefox htmlcov/index.html

migrate:
	@export APP_ENV=DEV && pipenv run python mono/manage.py migrate

makemigrations:
	@export APP_ENV=DEV && pipenv run python mono/manage.py makemigrations