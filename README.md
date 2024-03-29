[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)

[![Python](https://img.shields.io/badge/maintained%3F-yes-green.svg)](#)
[![Python](https://img.shields.io/website-up-down-green-red/https/rodrigokimura.com.svg)](https://rodrigokimura.com/)

[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

# Project Mono

## Inspiration

This project began as a playground for me to learn Python. 
It consists of a big Django project composed of a set of apps.  

## Stack

Main Python libs:
- Django
- Django REST Framework
- Pipenv
- Pytest
- Pylint
- Black

Other tools:
- SQLite for development database
- Fomantic-UI for frontend styling

# Setup development environment

## Install OS dependencies

### Debian based

```bash
sudo apt update
sudo apt upgrade
sudo apt install mariadb-client python-pip
```

### Arch based

```bash
sudo pacman -Syu
sudo pacman -S mariadb-client python-pip
```

## Install Pipenv (a Python dependency manager)

```bash
pip install pipenv
```

## Create local database

```bash
make clean-db
make migrate
```

## Create local superuser

```bash
make superuser
```

## Run local server

```bash
make devserver
```

## Main apps

### Finance

App to organize personal financial life by storing expenses and displaying charts.

#### Main models
```mermaid
classDiagram

    Transaction --> Category
    Transaction --* Account
    Budget --> Category

```

### Project Manager

App to manage projects using a kanban-style layout.

#### Main models
```mermaid
classDiagram

    Project *--> Board
    Board *--> Bucket
    Bucket *--> Card
    Card *--> File
    Card *--> Item
    Card o--> Tag
    Card o--> TimeEntry
    Bucket --> Theme
    Card --> Theme

```

### Notes

App to write notes using markdown syntax.

#### Main models
```mermaid
classDiagram
    Note o--> Tag
```

### Checklists

Simple to-do app.

#### Main models
```mermaid
classDiagram
    Checklist *--> Tasks
```

### Coder

Store snippets of code.

#### Main models
```mermaid
classDiagram
    Snippet o--> Tag
```

### Mind Maps

Create simple mind maps.

#### Main models
```mermaid
classDiagram
    MindMap *--> Node
```

### Pixel

App to insert a pixel for usage analytics.

#### Main models
```mermaid
classDiagram
    Site *--> Pings
```
