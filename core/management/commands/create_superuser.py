from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Creates the default admin superuser if it does not already exist'

    def handle(self, *args, **kwargs):
        if User.objects.filter(username='admin').exists():
            self.stdout.write(self.style.WARNING(
                'Superuser "admin" already exists — skipping creation.'
            ))
        else:
            User.objects.create_superuser(
                username='admin',
                email='admin@uiet.ac.in',
                password='admin123',
            )
            self.stdout.write(self.style.SUCCESS(
                'Superuser "admin" created successfully.'
            ))
