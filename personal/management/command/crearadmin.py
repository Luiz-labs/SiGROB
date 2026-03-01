from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = "Crea superusuario si no existe"

    def handle(self, *args, **kwargs):
        User = get_user_model()

        username = "admin"
        email = "admin@sigrob.com"
        password = "Admin123!"

        if not User.objects.filter(username=username).exists():
            self.stdout.write("Creando superusuario...")
            User.objects.create_superuser(username, email, password)
            self.stdout.write(self.style.SUCCESS("Superusuario creado"))
        else:
            self.stdout.write("Superusuario ya existe")