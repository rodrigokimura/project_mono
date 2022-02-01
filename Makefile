export PIPENV_VERBOSITY=-1
export PIPENV_IGNORE_VIRTUALENVS=1
export DJANGO_SETTINGS_MODULE=__mono.settings

RED		:= $(shell tput -Txterm setaf 1)
GREEN	:= $(shell tput -Txterm setaf 2)
ORANGE	:= $(shell tput -Txterm setaf 3)
BLUE	:= $(shell tput -Txterm setaf 4)
PURPLE	:= $(shell tput -Txterm setaf 5)
CYAN	:= $(shell tput -Txterm setaf 6)
WHITE	:= $(shell tput -Txterm setaf 7)
BOLD	:= $(shell tput bold)
DIM		:= $(shell tput dim)
RESET	:= $(shell tput -Txterm sgr0)

TARGET_MAX_CHAR_NUM=20

## Show help
help: art
	@echo ''
	@echo '${DIM}Usage:${RESET}'
	@echo '    ${GREY}make${RESET} ${CYAN}${BOLD}[target]${RESET}'
	@echo ''
	@echo '${DIM}Targets:${RESET}'
	@awk '/^[a-zA-Z\-0-9]+:/ { \
		helpMessage = match(lastLine, /^## (.*)/); \
		if (helpMessage) { \
			helpCommand = substr($$1, 0, index($$1, ":")-1); \
			helpMessage = substr(lastLine, RSTART + 3, RLENGTH); \
			printf "    ${CYAN}${BOLD}%-$(TARGET_MAX_CHAR_NUM)s${RESET} ${DIM}%s${RESET}\n", helpCommand, helpMessage; \
		} \
	} \
	{ lastLine = $$0 }' $(MAKEFILE_LIST)
	@echo ''

art:
	@echo '${GREEN}'
	@echo '█▀█ █▀█ █▀█ ░░█ █▀▀ █▀▀ ▀█▀   █▀▄▀█ █▀█ █▄░█ █▀█'
	@echo '█▀▀ █▀▄ █▄█ █▄█ ██▄ █▄▄ ░█░   █░▀░█ █▄█ █░▀█ █▄█'
	@echo '${RESET}'
	
# ========== CODE QUALITY ==================================================== #

BADGE=pipenv run genbadge
COV=pipenv run coverage
R_JUNIT=reports/junit/
R_COV=reports/coverage/
R_F8=reports/flake8/
R_PL=reports/pylint/

## Run all test suites, with multithreading and failfast
tests-ff:
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
	@echo 'Choose app from above:' \
		&& read APP \
		&& pipenv run pylint mono/$$APP --exit-zero

## Run tests on given app
test-app: list-apps
	@echo 'Choose app from above:' \
		&& read APP \
		&& export APP_ENV=TEST \
		&& export TEST_OUTPUT_VERBOSE=3 \
		&& export TEST_RUNNER=redgreenunittest.django.runner.RedGreenDiscoverRunner \
		&& cd mono \
		&& pipenv run python manage.py test -v 2 pylint $$APP --force-color

_tests:
	@export APP_ENV=TEST \
		&& cd mono \
		&& pipenv run python manage.py test -v 2 --force-color

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
flake8: _flake8
	@$(BADGE) flake8 -v -i mono/$(R_F8)flake8stats.txt -o mono/$(R_F8)flake8-badge.svg

## Run pylint and generate badge
pylint: _pylint
	@export score=$$(sed -n 's/^Your code has been rated at \([-0-9.]*\)\/.*/\1/p' mono/$(R_PL)pylint.txt) \
		&& echo "Pylint score was $$score" \
		&& pipenv run anybadge --value=$$score --file=mono/$(R_PL)pylint-badge.svg --label pylint -o

## Run all test suites and generate badge
tests: _tests _tests-badge

## Run all test suites with coverage and generate badge
coverage: _coverage _coverage-badge

## Run all quality checks, generating reports and badges
qa: art _isort flake8 pylint coverage _tests-badge

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


## Rollback to specific migration
rollback: list-apps
	@echo && read -p 'Choose app from above: ${BOLD}${CYAN}' APP \
		&& echo '${RESET}' \
		&& if ! test -d mono/$$APP; \
			then echo App '${RED}'$$APP'${RESET}' not found && exit 0; \
		fi \
		&& tree mono/$$APP/migrations --noreport -L 1 -P '*.py' -I '__*' \
		&& echo && read -p 'Choose the number of the migration target from above: ${BOLD}${CYAN}' MIGRATION \
		&& MIGRATION=$$(printf "%04d\n" $${MIGRATION}) && echo '${RESET}' \
		&& if test -f mono/$$APP/migrations/$$(ls mono/$$APP/migrations | grep $$MIGRATION); \
			then echo Selected migration: '${GREEN}'$$(ls mono/$$APP/migrations | grep $$MIGRATION)'${RESET}'\\n; \
			else echo '${RED}'Migration not found '${RESET}' && exit 0; \
		fi \
		&& $(DJANGO) migrate $$APP $$MIGRATION --plan \
		&& echo \
		&& read -p 'The operations shown above will be applied. ${BOLD}Are you sure?${RESET} [${GREEN}y${RESET}/${RED}N${RESET}] ${BOLD}${CYAN}' REPLY \
		&& echo \
		&& case "$$REPLY" in [Yy][Ee][Ss]|[Yy] ) \
			$(DJANGO) migrate $$APP $$MIGRATION ;; *) \
			echo '${RED}'Rollback canceled!'${RESET}' ;; \
		esac && echo && exit 0 

## Squash migrations
django-squash: list-apps
	@echo 'Choose app from above:' \
		&& read APP \
		&& echo Choose migration: \
		&& read MIGRATION \
		&& $(DJANGO) squashmigrations $$APP $$MIGRATION

# ========== DJANGO ========================================================== #


# ========== PIPENV ========================================================== #

install:
	@pipenv install

update:
	@pipenv update

# ========== PIPENV ========================================================== #


# ========== GIT ============================================================= #

## Stage, commit, bump version and push changes
commit: art
	@git add . 
	@pipenv run cz c
	@((pipenv run cz bump -ch) && (git push origin --tags) && (git push)) || (git push)

_pr: art
	@gh pr create \
		--fill \
		--base master \


_merge:
	@gh pr merge -m --auto

## Create pull request and set to auto-merge
pr: _pr _merge

## Pull changes
pull: art
	@git reset HEAD --hard
	@git fetch --tags -f
	@git pull

## Show last commit
last-commit:
	@echo '${RED}'$$(git log --pretty=format:"%H" -1 | grep -o '^[a-z0-9]*')'${RESET}'

PR_INFO_FILTER := 'title\|state\|author'

## Show state and checks of last pull request
check-pr:
	@LAST_PR=$$(gh pr list --state all --limit 1  | tail -n 1 | grep -o '^[0-9]*') \
		&& echo \
		&& echo '${DIM}Showing status for last PR:${RESET}''${RED}${BOLD}' $$LAST_PR '${RESET}' \
		&& echo \
		&& echo "$$(gh pr view $$LAST_PR | head -n 100 | grep ${PR_INFO_FILTER})" | awk 'BEGIN {FS = ":"} {printf "${CYAN}%-5s${RESET} %s\n", $$1, $$2}' \
		&& echo \
		&& gh pr checks $$LAST_PR || true \
		&& echo

mark-as-deployed:
	$(DJANGO) mark_as_deployed

## Connect to Production server
ssh: art
	@ssh kimura@ssh.pythonanywhere.com || true

build:
	@git checkout master
	@git reset HEAD --hard
	@git pull
	@pipenv install
	@pipenv run python mono/manage.py collectstatic --noinput
	@pipenv run python mono/manage.py makemigrations
	@pipenv run python mono/manage.py migrate
	@pipenv run python mono/manage.py mark_as_deployed
	@touch /var/www/www_monoproject_info_wsgi.py
	@tail /var/log/www.monoproject.info.server.log -n 100 --follow | grep 'www_monoproject_info_wsgi.py has been touched'


# ========== GIT ============================================================= #


# ==== EXPERIMENTAL FEATURES ====

copy-termux-shortcuts:
	@rm -r $(HOME)/.shortcuts/*
	@cp -a ./scripts/termux/. $(HOME)/.shortcuts/

list-apps:
	@tree mono -dL 1 -I _*\|reports\|htmlcov --noreport
