#!/usr/bin/env bash
# exit on error
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

python manage.py collectstatic --noinput

# Automatically create a superuser if environment variables are provided
python manage.py createsuperuser --noinput || true
