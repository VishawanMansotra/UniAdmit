from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Creates the default admin superuser if it does not already exist'

    def handle(self, *args, **kwargs):
        user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@uiet.ac.in',
                'is_staff': True,
                'is_superuser': True,
            },
        )

        if created:
            user.set_password('admin123')
            user.save()
            self.stdout.write(self.style.SUCCESS(
                'Superuser "admin" created successfully.'
            ))
        else:
            self.stdout.write(self.style.WARNING(
                'Superuser "admin" already exists — skipping creation.'
            ))
