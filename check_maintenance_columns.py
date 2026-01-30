
import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'swms.settings')
django.setup()

with connection.cursor() as cursor:
    cursor.execute("DESCRIBE hms_maintenancerequest")
    rows = cursor.fetchall()
    columns = [r[0] for r in rows]
    print(f"Columns in hms_maintenancerequest: {columns}")
    
    required = ['location', 'image', 'admin_notes', 'resolved_at']
    missing = [c for c in required if c not in columns]
    
    if missing:
        print(f"MISSING COLUMNS: {missing}")
        exit(1)
    else:
        print("All required columns present.")
