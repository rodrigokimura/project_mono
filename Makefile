export PIPENV_VERBOSITY=-1
export PIPENV_IGNORE_VIRTUALENVS=1
export DJANGO_SETTINGS_MODULE=__mono.settings

GREEN  := $(shell tput -Txterm setaf 2)
YELLOW := $(shell tput -Txterm setaf 3)
WHITE  := $(shell tput -Txterm setaf 7)
RESET  := $(shell tput -Txterm sgr0)

TARGET_MAX_CHAR_NUM=20

## Show help
help:
	@echo ''
	@echo 'Usage:'
	@echo '  ${YELLOW}make${RESET} ${GREEN}<target>${RESET}'
	@echo ''
	@echo 'Targets:'
	@awk '/^[a-zA-Z\-\_0-9]+:/ { \
		helpMessage = match(lastLine, /^## (.*)/); \
		if (helpMessage) { \
			helpCommand = substr($$1, 0, index($$1, ":")-1); \
			helpMessage = substr(lastLine, RSTART + 3, RLENGTH); \
			printf "  ${YELLOW}%-$(TARGET_MAX_CHAR_NUM)s${RESET} ${GREEN}%s${RESET}\n", helpCommand, helpMessage; \
		} \
	} \
	{ lastLine = $$0 }' $(MAKEFILE_LIST)
# ========== CODE QUALITY ==================================================== #

BADGE=pipenv run genbadge
COV=pipenv run coverage
R_JUNIT=reports/junit/
R_COV=reports/coverage/
R_F8=reports/flake8/
R_PL=reports/pylint/

## Run all test suites, with multithreading and failfast
qa-tests-ff:
	@export APP_ENV=TEST \
		&& cd mono \
		&& pipenv run python manage.py test --parallel 12 --failfast

_isort:
	@pipenv run isort mono

_flake8:
	@mkdir -p mono/$(R_F8)
	@cat /dev/null > mono/$(R_F8)flake8stats.txt
	@export APP_ENV=TEST && cd mono \
		&& pipenv run flake8 --statistics --tee --output-file $(R_F8)flake8stats.txt --exit-zero

_pylint:
	@mkdir -p mono/$(R_PL)
	@cat /dev/null > mono/$(R_PL)pylint.txt
	@pipenv run pylint --rcfile=.pylintrc --output-format=text mono | tee mono/$(R_PL)pylint.txt \

## Run pylint on given app
pylint-app: list-apps
	@echo Choose app: \
		&& read APP \
		&& pipenv run pylint mono/$$APP --exit-zero

_tests:
	@export APP_ENV=TEST \
		&& cd mono \
		&& pipenv run python manage.py test

_tests-badge:
	@$(BADGE) tests -v -i mono/$(R_JUNIT)junit.xml -o mono/$(R_JUNIT)junit-badge.svg

_coverage:
	@mkdir -p mono/$(R_COV)
	@cat /dev/null > mono/$(R_COV)coverage.xml
	@export APP_ENV=TEST && cd mono \
		&& $(COV) run --source='.' manage.py test -b --timing \
		&& $(COV) xml -o $(R_COV)coverage.xml \

_coverage-badge:
	@$(BADGE) coverage -v -i mono/$(R_COV)coverage.xml -o mono/$(R_COV)coverage-badge.svg

_open-coverage-report:
	@export APP_ENV=TEST && cd mono \
		&& $(COV) html \
		&& google-chrome htmlcov/index.html

## Run flake8 and generate badge
qa-flake8: _flake8
	@$(BADGE) flake8 -v -i mono/$(R_F8)flake8stats.txt -o mono/$(R_F8)flake8-badge.svg

## Run pylint and generate badge
qa-pylint: _pylint
	@export score=$$(sed -n 's/^Your code has been rated at \([-0-9.]*\)\/.*/\1/p' mono/$(R_PL)pylint.txt) \
		&& echo "Pylint score was $$score" \
		&& pipenv run anybadge --value=$$score --file=mono/$(R_PL)pylint-badge.svg --label pylint -o

## Run all test suites and generate badge
qa-tests: _tests _tests-badge

## Run all test suites with coverage and generate badge
qa-coverage: _coverage _coverage-badge

## Run all quality checks, generating reports and badges
qa: _isort qa-flake8 qa-pylint qa-coverage _tests-badge

# ========== CODE QUALITY ==================================================== #


# ========== DJANGO ========================================================== #

DJANGO=export APP_ENV=DEV && pipenv run python mono/manage.py

## Create superuser
django-superuser:
	@$(DJANGO) createsuperuser

## Run development server
django-devserver:
	@$(DJANGO) runserver 127.0.0.42:8080

## Write migration files
django-migrations:
	@$(DJANGO) makemigrations

## Apply all migrations
django-migrate:
	@$(DJANGO) migrate

# ========== DJANGO ========================================================== #


# ========== PIPENV ========================================================== #

install:
	@pipenv install

update:
	@pipenv update

# ========== PIPENV ========================================================== #


# ========== GIT ============================================================= #

## Stage, commit, bump version and push changes
commit:
	@git add . 
	@pipenv run cz c
	@pipenv run cz bump -ch
	@git push origin --tags
	@git push

## Create pull request
pr:
	@gh pr create \
		--fill \
		--base master \

## Pull changes
pull:
	@git reset HEAD --hard
	@git pull

## Show last commit
last-commit:
	@git log --pretty=format:"%H" -1 | grep -o '^[a-z0-9]*'

mark-as-deployed:
	$(DJANGO) mark_as_deployed

## Connect to Production server
ssh:
	@ssh kimura@ssh.pythonanywhere.com

# ========== GIT ============================================================= #


# ==== EXPERIMENTAL FEATURES ====

copy-termux-shortcuts:
	@rm -r $(HOME)/.shortcuts/*
	@cp -a ./scripts/termux/. $(HOME)/.shortcuts/

list-apps:
	@tree mono -dL 1 -I _*\|reports\|htmlcov