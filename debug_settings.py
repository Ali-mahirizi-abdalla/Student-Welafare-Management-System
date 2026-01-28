import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'swms.settings')

try:
    django.setup()
    print("Django setup successful!")
except Exception as e:
    print(f"Django setup failed: {e}")
    import traceback
    traceback.print_exc()

# Also try running system checks manually if setup works
if django.apps.apps.ready:
    from django.core.management import call_command
    try:
        call_command('check')
    except Exception as e:
        print(f"Check failed: {e}")
