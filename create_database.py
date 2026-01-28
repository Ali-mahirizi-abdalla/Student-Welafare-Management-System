"""
Quick database setup script for SWMS
Creates the MySQL database using Python
"""
import mysql.connector
from mysql.connector import Error

def create_database():
    try:
        # Connect to MySQL server
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='A8486aom@#'
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Create database
            cursor.execute("CREATE DATABASE IF NOT EXISTS swms_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print("✅ Database 'swms_db' created successfully!")
            
            # Verify
            cursor.execute("SHOW DATABASES LIKE 'swms_db'")
            result = cursor.fetchone()
            if result:
                print(f"✅ Verified: Database exists - {result[0]}")
            
            cursor.close()
            connection.close()
            return True
            
    except Error as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("Creating SWMS database...")
    if create_database():
        print("\n✅ Success! Now run: python manage.py migrate")
    else:
        print("\n❌ Failed to create database. Check your MySQL password and that MySQL is running.")
