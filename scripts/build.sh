#!/bin/bash
git reset HEAD --hard
git pull
python mono/manage.py collectstatic --noinput
python mono/manage.py makemigrations
python mono/manage.py migrate