web: python manage.py migrate --noinput && python manage.py seed_knowledge && python manage.py create_superuser && python manage.py collectstatic --noinput && gunicorn admission.wsgi:application
