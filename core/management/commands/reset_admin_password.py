from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Resets the admin superuser password using set_password() to ensure correct hashing'

    def handle(self, *args, **kwargs):
        try:
            user = User.objects.get(username='admin')
            user.set_password('admin123')
            user.save()
            self.stdout.write(self.style.SUCCESS(
                'Password for superuser "admin" has been reset successfully.'
            ))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(
                'Superuser "admin" does not exist. Run create_superuser first.'
            ))
