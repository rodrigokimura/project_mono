export PIPENV_VERBOSITY=-1
export PIPENV_IGNORE_VIRTUALENVS=1

help:
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z0-9_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)


# ========== CODE QUALITY ==================================================== #

BADGE=pipenv run genbadge
COV=pipenv run coverage
R_JUNIT=reports/junit/
R_COV=reports/coverage/
R_F8=reports/flake8/
R_PL=reports/pylint/

qa-tests-ff:  ## Run all test suites, with multithreading and failfast
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

qa-flake8: _flake8  ## Run flake8 and generate badge
	@$(BADGE) flake8 -v -i mono/$(R_F8)flake8stats.txt -o mono/$(R_F8)flake8-badge.svg

qa-pylint: _pylint  ## Run pylint and generate badge
	@export score=$$(sed -n 's/^Your code has been rated at \([-0-9.]*\)\/.*/\1/p' mono/$(R_PL)pylint.txt) \
		&& echo "Pylint score was $$score" \
		&& pipenv run anybadge --value=$$score --file=mono/$(R_PL)pylint-badge.svg --label pylint -o

qa-tests: _tests _tests-badge  ## Run all test suites and generate badge

qa-coverage: _coverage _coverage-badge  ## Run all test suites with coverage and generate badge

qa-full: _isort qa-flake8 qa-pylint qa-coverage _tests-badge  ## Run all quality checks, generating reports and badges

# ========== CODE QUALITY ==================================================== #


# ========== DJANGO ========================================================== #

DJANGO=export APP_ENV=DEV && pipenv run python mono/manage.py

django-superuser:  ## Create superuser
	@$(DJANGO) createsuperuser

django-devserver:  ## Run development server
	@$(DJANGO) runserver 127.0.0.42:8080

django-migrations:  ## Write migration files
	@$(DJANGO) makemigrations

django-migrate:  ## Apply all migrations
	@$(DJANGO) migrate

# ========== DJANGO ========================================================== #


# ========== PIPENV ========================================================== #

install:
	@pipenv install

update:
	@pipenv update

# ========== PIPENV ========================================================== #


# ========== GIT ============================================================= #

commit:  ## Stage, commit, bump version and push changes
	@git add . 
	@cz c
	@cz bump -ch
	@git push origin --tags
	@git push

pull-request:  ## Create pull request
	@gh pr create \
		--fill \
		--base master \

pull:  ## Pull changes
	@git reset HEAD --hard
	@git pull

last-commit:  ## Show last commit
	@git log --pretty=format:"%H" -1 | grep -o '^[a-z0-9]*'

mark-as-deployed:
	$(DJANGO) mark_as_deployed

ssh:
	@ssh kimura@ssh.pythonanywhere.com

# ========== GIT ============================================================= #


# ==== EXPERIMENTAL FEATURES ====

copy-termux-shortcuts:
	@rm -r $(HOME)/.shortcuts/*
	@cp -a ./scripts/termux/. $(HOME)/.shortcuts/