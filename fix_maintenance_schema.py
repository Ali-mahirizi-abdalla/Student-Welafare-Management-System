import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'swms.settings')
django.setup()

with connection.cursor() as cursor:
    # Fetch columns
    cursor.execute("DESCRIBE hms_maintenancerequest")
    cols = [r[0] for r in cursor.fetchall()]
    print(f"Current columns: {cols}")

    # 1. Add location (required)
    try:
        if 'location' not in cols:
            print("Adding location...")
            cursor.execute("ALTER TABLE hms_maintenancerequest ADD COLUMN location VARCHAR(100) NOT NULL DEFAULT 'Unknown'")
        else:
            print("location already exists.")
    except Exception as e:
        print(f"Error adding location: {e}")

    # 2. Add image
    try:
        if 'image' not in cols:
            print("Adding image...")
            cursor.execute("ALTER TABLE hms_maintenancerequest ADD COLUMN image VARCHAR(100)")
        else:
            print("image already exists.")
    except Exception as e:
        print(f"Error adding image: {e}")

    # 3. Add admin_notes
    try:
        if 'admin_notes' not in cols:
            print("Adding admin_notes...")
            cursor.execute("ALTER TABLE hms_maintenancerequest ADD COLUMN admin_notes LONGTEXT")
        else:
            print("admin_notes already exists.")
    except Exception as e:
        print(f"Error adding admin_notes: {e}")

    # 4. Add resolved_at
    try:
        if 'resolved_at' not in cols:
            print("Adding resolved_at...")
            cursor.execute("ALTER TABLE hms_maintenancerequest ADD COLUMN resolved_at DATETIME NULL")
        else:
            print("resolved_at already exists.")
    except Exception as e:
        print(f"Error adding resolved_at: {e}")

    # 5. Drop photo (if exists)
    try:
        if 'photo' in cols:
            print("Dropping photo...")
            cursor.execute("ALTER TABLE hms_maintenancerequest DROP COLUMN photo")
    except Exception as e:
        print(f"Error dropping photo: {e}")

print("Schema update complete.")
