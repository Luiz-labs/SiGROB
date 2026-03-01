import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sigro_core.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = "admin"
email = "admin@sigrob.com"
password = "Admin123!"

if not User.objects.filter(username=username).exists():
    print("Creando superusuario...")
    User.objects.create_superuser(username, email, password)
    print("Superusuario creado")
else:
    print("El superusuario ya existe")