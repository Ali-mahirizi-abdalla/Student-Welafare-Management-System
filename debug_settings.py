
import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'swms.settings')
django.setup()

print("--- DEBUG SETTINGS ---")
try:
    print(f"DBBACKUP_STORAGE: {getattr(settings, 'DBBACKUP_STORAGE', 'NOT FOUND')}")
    print(f"DBBACKUP_STORAGE_OPTIONS: {getattr(settings, 'DBBACKUP_STORAGE_OPTIONS', 'NOT FOUND')}")
except Exception as e:
    print(f"Error accessing backup settings: {e}")

if 'dbbackup' in settings.INSTALLED_APPS:
    print("APP: dbbackup found in INSTALLED_APPS")
else:
    print("APP: dbbackup NOT found in INSTALLED_APPS")
print("----------------------")
