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


##@ Misc

help: art  ## Show help
	@awk 'BEGIN \
		{ \
			FS = ":.*##"; \
			print "${DIM}Usage:${RESET}"; \
			print "    ${GREY}make${RESET} ${CYAN}${BOLD}[target]${RESET}\n"; \
			print "${DIM}Targets:${RESET}"; \
		} \
		/^[a-zA-Z_-]+:.*?##/ \
		{ \
			printf "  ${CYAN}${BOLD}%-10s${RESET} ${DIM}%s${RESET}\n", $$1, $$2; \
		} \
		/^##@/ \
		{ \
			printf "\n${BLUE}${BOLD}%-$(TARGET_MAX_CHAR_NUM)s${RESET} \n", toupper(substr($$0, 5)); \
		}' $(MAKEFILE_LIST)
	@echo

art:
	@echo '${GREEN}'
	@echo '█▀█ █▀█ █▀█ ░░█ █▀▀ █▀▀ ▀█▀   █▀▄▀█ █▀█ █▄░█ █▀█'
	@echo '█▀▀ █▀▄ █▄█ █▄█ ██▄ █▄▄ ░█░   █░▀░█ █▄█ █░▀█ █▄█'
	@echo '${RESET}'


##@ Code quality

BADGE=pipenv run genbadge
# BADGE=pipenv run anybadge
COV=pipenv run coverage
R_COV=reports/coverage
R_F8=reports/flake8
R_PL=reports/pylint
R_PT=reports/pytest

isort:  ## Run isort
	@pipenv run isort mono

flake8:  ## Run flake8
	@mkdir -p mono/$(R_F8)
	@cat /dev/null > mono/$(R_F8)/flake8stats.txt
	@export APP_ENV=TEST && cd mono \
		&& pipenv run flake8 --statistics --tee --output-file $(R_F8)/flake8stats.txt --exit-zero

pylint:  ## Run pylint
	@mkdir -p mono/$(R_PL)
	@touch mono/$(R_PL)/report.json
	@cat /dev/null > mono/$(R_PL)/report.json
	@pipenv run pylint mono \
		--rcfile=.pylintrc \
		--output-format=json:mono/$(R_PL)/report.json,colorized

pylint-app: list-apps  ## Run pylint on given app
	@echo 'Choose app from above:' \
		&& read APP \
		&& pipenv run pylint mono/$$APP --exit-zero

_upload-pylint-report:
	@curl $(MONO_URL)/hc/api/pylint/ \
		-X POST \
		-H 'Authorization: Token $(MONO_TOKEN)' \
		-F report_file=@./mono/$(R_PL)/report.json

test-app: list-apps  ## Run tests on given app
	@echo && read -p 'Choose app from above: ${BOLD}${CYAN}' APP \
		&& echo '${RESET}' \
		&& if ! test -d mono/$$APP; \
			then echo App '${RED}'$$APP'${RESET}' not found && exit 0; \
		fi \
		&& export APP_ENV=TEST \
		&& cd mono \
		&& pipenv run pytest $$APP

test:
	@mkdir -p mono/$(R_PT)
	@touch mono/$(R_PT)/report.json
	@cat /dev/null > mono/$(R_PT)/report.json
	@export APP_ENV=TEST \
		&& cd mono \
		&& pipenv run pytest --report-log=$(R_PT)/report.json

_upload-pytest-report:
	@curl $(MONO_URL)/hc/api/pytest/ \
		-X POST \
		-H 'Authorization: Token $(MONO_TOKEN)' \
		-F report_file=@./mono/$(R_PT)/report.json

coverage:
	@mkdir -p mono/$(R_PT)
	@mkdir -p mono/$(R_COV)
	@touch mono/$(R_PT)/report.json
	@touch mono/$(R_COV)/report.json
	@cat /dev/null > mono/$(R_PT)/report.json
	@cat /dev/null > mono/$(R_COV)/report.json
	@export APP_ENV=TEST && cd mono \
		&& pipenv run pytest --cov=. --report-log=$(R_PT)/report.json \
		&& $(COV) json -o $(R_COV)/report.json

_upload-coverage-report:
	@curl $(MONO_URL)/hc/api/coverage/ \
		-X POST \
		-H 'Authorization: Token $(MONO_TOKEN)' \
		-F report_file=@./mono/$(R_COV)/report.json

_open-coverage-report:
	@export APP_ENV=TEST && cd mono \
		&& $(COV) html \
		&& google-chrome htmlcov/index.html

diagrams:
	@mkdir diagrams
	@cd mono \
		&& ls -1 -d */ \
		| grep -v '__\|_' \
		| grep -o '[a-z]*' \
		| while read APP ; \
			do pipenv run pyreverse $$APP --output=mmd --project=$$APP ; \
		done \
		&& mv *.mmd ../diagrams/

# pylint: _pylint  ## Run pylint and generate badge
# 	@export score=$$(sed -n 's/^Your code has been rated at \([-0-9.]*\)\/.*/\1/p' mono/$(R_PL)pylint.txt) \
# 		&& echo "Pylint score was $$score" \
# 		&& pipenv run anybadge --value=$$score --file=mono/$(R_PL)pylint-badge.svg --label pylint -o

# qa: art _isort flake8 pylint coverage _tests-badge  ## Run all quality checks, generating reports and badges
qa: art isort flake8 pylint coverage  ## Run all quality checks, generating reports and badges

upload-reports: _upload-pylint-report _upload-coverage-report _upload-pytest-report

##@ Django

DJANGO=export APP_ENV=DEV && pipenv run python mono/manage.py

superuser:  ## Create superuser
	@$(DJANGO) createsuperuser

devserver:  ## Run development server
	@$(DJANGO) runserver 127.0.0.42:8080

clean-db:  ## Delete sqlite database
	@rm mono/db.sqlite3

migrations:  ## Write migration files
	@$(DJANGO) makemigrations

empty-migrations: list-apps  ## Write empty migration file
	@echo && read -p 'Choose app from above: ${BOLD}${CYAN}' APP \
		&& echo '${RESET}' \
		&& if ! test -d mono/$$APP; \
			then echo App '${RED}'$$APP'${RESET}' not found && exit 0; \
		fi \
		&& $(DJANGO) makemigrations $$APP --empty \
		&& echo && exit 0 

migrate:  ## Apply all migrations
	@$(DJANGO) migrate

rollback: list-apps  ## Rollback to specific migration
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

squash: list-apps  ## Squash migrations
	@echo 'Choose app from above:' \
		&& read APP \
		&& echo Choose migration: \
		&& read MIGRATION \
		&& $(DJANGO) squashmigrations $$APP $$MIGRATION

translation:  ## Squash migrations
	@$(DJANGO) makemessages -a

translate:  ## Squash migrations
	@$(DJANGO) compilemessages


##@ Pipenv

install:  ## Install dependencies
	@pipenv install

update:  ## Update dependencies
	@pipenv update

##@ Dev worflow

pull: art  ## Pull changes
	@git reset HEAD --hard
	@git fetch --tags -f
	@git pull

commit: art  ## Stage, commit, bump version and push changes
	@git add . 
	@pipenv run cz c
	@((pipenv run cz bump -ch) && (git push origin --tags) && (git push)) || (git push)

_pr: art
	@gh pr create \
		--fill \
		--base master

_merge:
	@gh pr merge -m --auto

pr: _pr _merge  ## Create pull request and set to auto-merge

PR_INFO_FILTER := 'title\|state\|author'

check:  ## Show state and checks of last pull request
	@LAST_PR=$$(gh pr list --state all --limit 1  | tail -n 1 | grep -o '^[0-9]*') \
		&& echo \
		&& echo '${DIM}Showing status for last PR:${RESET}''${BLUE}${BOLD}' $$LAST_PR '${RESET}' \
		&& echo \
		&& echo "$$(gh pr view $$LAST_PR | head -n 10 | grep ${PR_INFO_FILTER})" | \
			awk 'BEGIN \
				{ \
					FS = ":\t"; \
					format = "${CYAN}%-7s${RESET} %s\n"; \
				} \
				{ \
					if 			($$1 ~ /state/ && $$2 ~ /MERGED/) 	{ value = "${PURPLE}MERGED ✓${RESET}"; } \
					else if 	($$1 ~ /state/ && $$2 ~ /OPEN/) 	{ value = "${GREEN}OPEN ↺${RESET}"; } \
					else { value = $$2; } \
					printf format, $$1, value \
				}' \
		&& echo \
		&& echo "$$(gh pr checks $$LAST_PR)" | \
			awk 'BEGIN \
				{ \
					FS = "\t"; \
					format = "${CYAN}%-7s${RESET} %s %7s ${DIM}%s${RESET}\n"; \
				} \
				{ \
					if 			($$2 ~ /pass/) 		{ status = "${GREEN}pass ✓     ${RESET}"; } \
					else if 	($$2 ~ /pending/) 	{ status = "${ORANGE}pending *  ${RESET}"; } \
					else if 	($$2 ~ /fail/) 		{ status = "${RED}fail ✗     ${RESET}"; } \
					else 							{ status = $$2; } \
					printf format, $$1, status, $$3, $$4; \
				}'
		@echo

ssh: art  ## Connect to Production server
	@ssh kimura@ssh.pythonanywhere.com || true

mark-as-deployed:
	$(DJANGO) mark_as_deployed

init:  ## Populate initial data
	$(DJANGO) mark_as_deployed

last-commit:
	@echo '${RED}'$$(git log --pretty=format:"%H" -1 | grep -o '^[a-z0-9]*')'${RESET}'

build:  ## Execute commands to build app in production
	@git checkout master
	@git reset HEAD --hard
	@git pull
	@pipenv install
	@pipenv run python mono/manage.py collectstatic --noinput
	@pipenv run python mono/manage.py makemigrations
	@pipenv run python mono/manage.py migrate
	@pipenv run python mono/manage.py mark_as_deployed
	@touch /var/www/www_monoproject_info_wsgi.py
	@tail /var/log/www.monoproject.info.server.log -n 100 --follow | grep 'www_monoproject_info_wsgi.py has been touched' || true

copy-termux-shortcuts:
	@rm -r $(HOME)/.shortcuts/*
	@cp -a ./scripts/termux/. $(HOME)/.shortcuts/

list-apps:
	@tree mono -dL 1 -I _*\|reports\|htmlcov --noreport
