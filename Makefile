copy-termux-shortcuts:
	@rm -r $(HOME)/.shortcuts/*
	@cp -a ./scripts/termux/. $(HOME)/.shortcuts/

test:
	@export APP_ENV=TEST && cd mono && pipenv run python manage.py test --parallel 12 --failfast

cov:
	@export APP_ENV=TEST && cd mono && pipenv run coverage run --source='.' manage.py test -b --timing \
		&& pipenv run coverage xml -o reports/coverage/coverage.xml \
		&& pipenv run coverage html \
		&& firefox htmlcov/index.html

generate-badges: flake8 cov
	@export APP_ENV=TEST && cd mono \
		&& pipenv run genbadge tests -v -i reports/junit/junit.xml -o reports/junit/junit-badge.svg \
		&& pipenv run genbadge coverage -v -i reports/coverage/coverage.xml -o reports/coverage/coverage-badge.svg \
		&& pipenv run genbadge flake8 -v -i reports/flake8/flake8stats.txt -o reports/flake8/flake8-badge.svg


flake8:
	@export APP_ENV=TEST && cd mono \
		&& pipenv run flake8 --statistics --tee --output-file reports/flake8/flake8stats.txt --exit-zero

migrate:
	@export APP_ENV=DEV && pipenv run python mono/manage.py migrate

makemigrations:
	@export APP_ENV=DEV && pipenv run python mono/manage.py makemigrations