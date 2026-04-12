import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
import django
django.setup()
from django.contrib.auth.models import User
from django.test import Client

print('=== USERS IN DB ===')
for u in User.objects.all():
    print(f'ID: {u.id}, Username: {u.username}, Email: {u.email}, Superuser: {u.is_superuser}, Password Set: {u.has_usable_password()}')

print('\n=== TESTING REGISTRATION ===')
c = Client()
data = {'username': 'testuser123', 'password': 'testpass123', 'email': 'test@example.com'}
resp = c.post('/api/register/', data)
print(f'Register Status: {resp.status_code}')
print(f'Register Response: {resp.content.decode()}')

print('\n=== TESTING LOGIN ===')
resp2 = c.post('/api/login/', {'username': 'testuser123', 'password': 'testpass123'})
print(f'Login Status: {resp2.status_code}')
print(f'Login Response: {resp2.content.decode()}')