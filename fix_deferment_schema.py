import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'swms.settings')
django.setup()

with connection.cursor() as cursor:
    # Fetch columns once
    cursor.execute("DESCRIBE hms_defermentrequest")
    cols = [r[0] for r in cursor.fetchall()]
    print(f"Current columns: {cols}")

    # 1. Rename leave_type to deferment_type
    try:
        if 'leave_type' in cols:
            print("Renaming leave_type to deferment_type...")
            cursor.execute("ALTER TABLE hms_defermentrequest CHANGE leave_type deferment_type VARCHAR(30) NOT NULL")
        elif 'deferment_type' in cols:
             print("deferment_type already exists.")
        else:
             print("Neither leave_type nor deferment_type found! Creating deferment_type.")
             cursor.execute("ALTER TABLE hms_defermentrequest ADD COLUMN deferment_type VARCHAR(30) NOT NULL DEFAULT 'fee_challenges'")
    except Exception as e:
        print(f"Error handling deferment_type: {e}")

    # 2. Add admin_response
    try:
        if 'admin_response' not in cols:
             print("Adding admin_response...")
             cursor.execute("ALTER TABLE hms_defermentrequest ADD COLUMN admin_response LONGTEXT")
        else:
             print("admin_response already exists.")
    except Exception as e:
         print(f"Error handling admin_response: {e}")

    # 3. Drop supporting_documents
    try:
        if 'supporting_documents' in cols:
             print("Dropping supporting_documents...")
             cursor.execute("ALTER TABLE hms_defermentrequest DROP COLUMN supporting_documents")
        else:
             print("supporting_documents not found.")
    except Exception as e:
         print(f"Error dropping supporting_documents: {e}")
    
    # Check for other columns to drop
    cols_to_drop = ['admin_notes', 'reviewed_at', 'contact_during_deferment', 'other_reason_detail']
    for col in cols_to_drop:
        if col in cols:
             try:
                 print(f"Dropping {col}...")
                 cursor.execute(f"ALTER TABLE hms_defermentrequest DROP COLUMN {col}")
             except Exception as e:
                 print(f"Error dropping {col}: {e}")

    print("Schema update complete.")
