#!/usr/bin/env bash
# exit on error
set -o errexit

pip install cryptography
pip install -r requirements.txt

python manage.py collectstatic --noinput
python manage.py migrate --fake library 0001_initial --noinput || true
python manage.py migrate --noinput
