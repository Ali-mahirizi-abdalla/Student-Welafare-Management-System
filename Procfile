web: python fix_library_migrations.py && python manage.py migrate --noinput && gunicorn swms.wsgi --log-file -
worker: celery -A swms worker --loglevel=info
beat: celery -A swms beat --loglevel=info
