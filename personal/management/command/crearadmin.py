from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Crea usuario admin si no existe'

    def handle(self, *args, **kwargs):
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@sigrob.com',
                password='Admin123!'
            )
            self.stdout.write(self.style.SUCCESS('Admin creado'))
        else:
            self.stdout.write('Admin ya existe')