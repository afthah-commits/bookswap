import os
import django

# Set Django settings module before importing anything
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "book_exchange.settings")
django.setup()  # Initialize Django

from django.contrib.auth.models import User

# Get superuser info from environment
USERNAME = os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin")
EMAIL = os.environ.get("DJANGO_SUPERUSER_EMAIL", "admin@example.com")
PASSWORD = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "admin123")

# Create superuser if it doesn't exist
if not User.objects.filter(username=USERNAME).exists():
    User.objects.create_superuser(USERNAME, EMAIL, PASSWORD)
    print(f"Superuser {USERNAME} created!")
else:
    print(f"Superuser {USERNAME} already exists.")
