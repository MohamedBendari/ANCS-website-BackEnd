import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
import django
django.setup()
from django.contrib.auth.models import User
print('COUNT', User.objects.count())
for u in User.objects.all():
    print('USER', u.username, u.email, u.is_superuser, u.has_usable_password())
