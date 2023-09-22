#!/bin/bash
git reset HEAD --hard
git pull
python mono/manage.py collectstatic --noinput
python mono/manage.py makemigrations
python mono/manage.py migrate
python mono/manage.py mark_as_deployed
touch /var/www/www_monoproject_info_wsgi.py
tail /var/log/rodrigokimura.com.server.log -n 100 --follow