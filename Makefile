export PIPENV_VERBOSITY=-1

copy-termux-shortcuts:
	@rm -r $(HOME)/.shortcuts/*
	@cp -a ./scripts/termux/. $(HOME)/.shortcuts/


test: 
	@export APP_ENV=TEST && cd mono && pipenv run python manage.py test --parallel 12 --failfast

cov: 
	@cat /dev/null > mono/reports/coverage/coverage.xml
	@export APP_ENV=TEST && cd mono && pipenv run coverage run --source='.' manage.py test -b --timing \
		&& pipenv run coverage xml -o reports/coverage/coverage.xml \
		&& pipenv run coverage html \
		&& firefox htmlcov/index.html

flake8: 
	@cat /dev/null > mono/reports/flake8/flake8stats.txt
	@export APP_ENV=TEST && cd mono \
		&& pipenv run flake8 --statistics --tee --output-file reports/flake8/flake8stats.txt --exit-zero

generate-badges: flake8 cov
	@export APP_ENV=TEST && cd mono \
		&& pipenv run genbadge tests -v -i reports/junit/junit.xml -o reports/junit/junit-badge.svg \
		&& pipenv run genbadge coverage -v -i reports/coverage/coverage.xml -o reports/coverage/coverage-badge.svg \
		&& pipenv run genbadge flake8 -v -i reports/flake8/flake8stats.txt -o reports/flake8/flake8-badge.svg

migrate:
	@export APP_ENV=DEV && pipenv run python mono/manage.py migrate

makemigrations:
	@export APP_ENV=DEV && pipenv run python mono/manage.py makemigrations

runserver:
	@export APP_ENV=DEV && pipenv run python mono/manage.py runserver 127.0.0.42:8080