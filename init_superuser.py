#!/usr/bin/env python
"""
Standalone script to create the default admin superuser.

Run manually when needed:
    python init_superuser.py

This is a convenience wrapper around the management command and can be
executed directly without going through `manage.py`.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admission.settings')
django.setup()

from django.contrib.auth.models import User  # noqa: E402 — must come after setup()

USERNAME = 'admin'
EMAIL = 'admin@uiet.ac.in'
PASSWORD = 'admin123'

user, created = User.objects.get_or_create(
    username=USERNAME,
    defaults={
        'email': EMAIL,
        'is_staff': True,
        'is_superuser': True,
    },
)

if created:
    user.set_password(PASSWORD)
    user.save()
    print(f'[OK] Superuser "{USERNAME}" created successfully.')
else:
    print(f'[--] Superuser "{USERNAME}" already exists — skipping creation.')
