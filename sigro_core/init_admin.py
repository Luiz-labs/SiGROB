import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sigro_core.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = os.environ.get("ADMIN_USER", "admin")
email = os.environ.get("ADMIN_EMAIL", "admin@sigrob.com")
password = os.environ.get("ADMIN_PASSWORD", "Admin123!")

if not User.objects.filter(username=username).exists():
    print("Creando superusuario admin...")
    User.objects.create_superuser(username, email, password)
    print("Superusuario creado")
else:
    print("Superusuario ya existe")