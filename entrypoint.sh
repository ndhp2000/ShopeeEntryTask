#!/bin/sh

python manage.py migrate --no-input

gunicorn EventManager.wsgi:application --preload --bind 0.0.0.0:8000 --workers 8 --threads 2