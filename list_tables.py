import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'swms.settings')
django.setup()

with connection.cursor() as cursor:
    cursor.execute("SHOW TABLES LIKE 'hms%'")
    tables = cursor.fetchall()
    print("HMS Tables:")
    for table in tables:
        print(table[0])
