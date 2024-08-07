#!/bin/sh

echo 'Running migrations...'
python manage.py migrate
echo 'Collecting static files...'
python manage.py collectstatic --no-input
gunicorn --bind 0.0.0.0:8000 config.wsgi

exec "$@"