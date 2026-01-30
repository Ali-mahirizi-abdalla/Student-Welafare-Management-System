import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'swms.settings')
django.setup()
from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("SHOW TABLES LIKE 'hms_suggestion'")
    res = cursor.fetchone()
    if res:
        print("STATUS: FOUND")
    else:
        print("STATUS: MISSING")
        cursor.execute('CREATE TABLE hms_suggestion (id bigint AUTO_INCREMENT PRIMARY KEY, content longtext NOT NULL, created_at datetime(6) NOT NULL, is_read tinyint(1) NOT NULL DEFAULT 0);')
        print("CREATED")
