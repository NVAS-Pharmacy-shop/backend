#!/bin/sh

python manage.py makemigrations
python manage.py migrate

python manage.py collectstatic --noinput

gunicorn --bind 0.0.0.0:3000 --workers 3 nvasshop.wsgi:application


