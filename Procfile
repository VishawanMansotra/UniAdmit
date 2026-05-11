web: python manage.py collectstatic --noinput && python manage.py migrate --noinput && python manage.py create_superuser && gunicorn admission.wsgi:application
