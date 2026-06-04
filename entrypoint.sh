#!/bin/bash
set -e

python manage.py collectstatic --no-input
python manage.py migrate

exec gunicorn djangocrud.wsgi --bind 0.0.0.0:8000 --workers 2 --log-file -
