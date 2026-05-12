web: python manage.py migrate --noinput && python manage.py seed_knowledge && python manage.py collectstatic --noinput && gunicorn admission.wsgi:application
