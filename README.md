[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)

[![Python](https://img.shields.io/badge/maintained%3F-yes-green.svg)](#)
[![Python](https://img.shields.io/website-up-down-green-red/https/www.monoproject.info.svg)](https://www.monoproject.info/)

[![Flake8 Status](mono/reports/flake8/flake8-badge.svg?dummy=8484744)](#)
[![Pylint Status](mono/reports/pylint/pylint-badge.svg?dummy=8484744)](#)
[![Tests Status](mono/reports/junit/junit-badge.svg?dummy=8484744)](#)
[![Coverage Status](mono/reports/coverage/coverage-badge.svg?dummy=8484744)](#)

[![Python application](https://github.com/rodrigokimura/project_mono/actions/workflows/python-app.yml/badge.svg)](https://github.com/rodrigokimura/project_mono/actions/workflows/python-app.yml)

[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

# Project Mono

## Instructions to setup development environment
- Install Python 3.8+
- Or check your python version using `python -V`
- run `pip install -r requirements.txt`

### Experimental Android (Termux) environment
- For `social-auth-app-django` package:
    - `pkg install make`
    - `pkg install libffi`
    - `pkg install libcrypt`
    - `pkg install clang`
    - `pkg install rust`
    - `pkg install openssl`
    - `pkg install mariadb`
    - `pkg install libjpeg-turbo`
    - `pkg install libxml2`
    - `pkg install libxslt`
    - `CFLAGS="-O0" pipenv install lxml`
    - `LDFLAGS="-L/opt/local/lib" CFLAGS="-I/opt/local/include" pipenv install cryptography`

<!-- dummy text -->

## Useful links
- [Django documentation](https://docs.djangoproject.com/en/3.2/)
- [Fomantic-UI](https://fomantic-ui.com/)
- [Django Tutorial in Visual Studio Code](https://code.visualstudio.com/docs/python/tutorial-django)
- [DB Browser for SQLite](https://sqlitebrowser.org/)
