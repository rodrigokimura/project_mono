export PIPENV_VERBOSITY=-1
export PIPENV_IGNORE_VIRTUALENVS=1

.PHONY: help

help:
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

lint: ## Run linter
	@pipenv run isort mono
	@pipenv run flake8
	@pipenv run pylint mono

test:  ## Run all test suites
	@export APP_ENV=TEST \
		&& cd mono \
		&& pipenv run python manage.py test --parallel 12 --failfast

cov:  ## Run all test suites with coverage
	@cat /dev/null > mono/reports/coverage/coverage.xml
	@export APP_ENV=TEST && cd mono && pipenv run coverage run --source='.' manage.py test -b --timing \
		&& pipenv run coverage xml -o reports/coverage/coverage.xml \
		&& pipenv run coverage html \
		&& firefox htmlcov/index.html

flake8: 
	@cat /dev/null > mono/reports/flake8/flake8stats.txt
	@export APP_ENV=TEST && cd mono \
		&& pipenv run flake8 --statistics --tee --output-file reports/flake8/flake8stats.txt --exit-zero

generate-badges: flake8 cov  ## Generate badges for flake8 and coverage
	@export APP_ENV=TEST && cd mono \
		&& pipenv run genbadge tests -v -i reports/junit/junit.xml -o reports/junit/junit-badge.svg \
		&& pipenv run genbadge coverage -v -i reports/coverage/coverage.xml -o reports/coverage/coverage-badge.svg \
		&& pipenv run genbadge flake8 -v -i reports/flake8/flake8stats.txt -o reports/flake8/flake8-badge.svg

migrate:  ## Apply all migrations
	@export APP_ENV=DEV && pipenv run python mono/manage.py migrate

makemigrations:  ## Write migration files
	@export APP_ENV=DEV && pipenv run python mono/manage.py makemigrations

runserver:  ## Run development server
	@export APP_ENV=DEV && pipenv run python mono/manage.py runserver 127.0.0.42:8080

commit:  ## Stage, commit and push changes
	@echo "Message: "; \
  read MESSAGE; \
  git add .; \
  git commit -m "$$MESSAGE"; \
  git push


# ==== EXPERIMENTAL FEATURES ====

copy-termux-shortcuts:
	@rm -r $(HOME)/.shortcuts/*
	@cp -a ./scripts/termux/. $(HOME)/.shortcuts/