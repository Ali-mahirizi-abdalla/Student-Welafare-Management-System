import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'swms.settings')
django.setup()

with connection.cursor() as cursor:
    cursor.execute("DESCRIBE hms_leaverequest")
    rows = cursor.fetchall()
    print([r[0] for r in rows])
