import os
import django
import traceback
from django.conf import settings
from django.core.management import call_command

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'swms.settings')
os.environ['USE_SQLITE'] = 'True'
django.setup()

# Run migrations for the SQLite database
print("Running migrations...")
try:
    call_command('migrate', verbosity=0, interactive=False)
except Exception as e:
    print(f"Migration failed: {e}")

from django.contrib.auth.models import User
from hms.backends import EmailBackend

def verify_email_backend():
    print("Verifying EmailBackend...")
    backend = EmailBackend()
    
    # Use a dummy password for testing
    password = 'TestPassword123!'
    
    # 1. Create a test user (cleanly)
    test_email = 'verify_email@example.com'
    test_username = 'verify_user'
    
    try:
        # Cleanup if exists
        User.objects.filter(email=test_email).delete()
        User.objects.filter(username=test_username).delete()
        
        user = User.objects.create_user(
            username=test_username,
            email=test_email,
            password=password
        )
        print(f"Created test user: {test_username} / {test_email}")
        
        # Test Case 1: Authenticate with username
        auth_user = backend.authenticate(None, username=test_username, password=password)
        if auth_user and auth_user.pk == user.pk:
            print("Success: Authenticated with username.")
        else:
            print("Failure: Could not authenticate with username.")
            
        # Test Case 2: Authenticate with email
        auth_user = backend.authenticate(None, username=test_email, password=password)
        if auth_user and auth_user.pk == user.pk:
            print("Success: Authenticated with email.")
        else:
            print("Failure: Could not authenticate with email.")
            
        # Test Case 3: Invalid password
        auth_user = backend.authenticate(None, username=test_email, password='wrong_password')
        if auth_user is None:
            print("Success: Correctly failed with wrong password.")
        else:
            print("Failure: Authenticated even with wrong password!")
            
        # Cleanup
        user.delete()
        print("Cleanup done.")

    except Exception as e:
        print("An error occurred during verification:")
        traceback.print_exc()
        # Ensure cleanup if user was created
        User.objects.filter(email=test_email).delete()

if __name__ == "__main__":
    verify_email_backend()
