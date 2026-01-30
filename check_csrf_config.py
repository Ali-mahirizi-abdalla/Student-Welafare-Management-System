import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'swms.settings')
django.setup()

from django.conf import settings

print("=== CSRF Configuration ===")
print(f"CSRF_TRUSTED_ORIGINS: {settings.CSRF_TRUSTED_ORIGINS}")
print(f"CSRF_COOKIE_SECURE: {settings.CSRF_COOKIE_SECURE}")
print(f"CSRF_COOKIE_HTTPONLY: {settings.CSRF_COOKIE_HTTPONLY}")
print(f"CSRF_COOKIE_SAMESITE: {settings.CSRF_COOKIE_SAMESITE}")
print(f"CSRF_USE_SESSIONS: {getattr(settings, 'CSRF_USE_SESSIONS', False)}")
print(f"DEBUG: {settings.DEBUG}")
print(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
