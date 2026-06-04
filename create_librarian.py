import os
import django

# Ensure the settings module is set for Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'swms.settings')
# Setup Django
django.setup()

from django.contrib.auth import get_user_model
from hms.models import StaffProfile

User = get_user_model()

# Create or get the librarian user
user, created = User.objects.get_or_create(
    username='librarian',
    defaults={'email': 'lib@campus.com'}
)
user.is_staff = True
user.set_password('lib123')
user.save()

# Create or update the staff profile for the librarian role
profile, p_created = StaffProfile.objects.get_or_create(
    user=user,
    defaults={'role': 'librarian', 'national_id': 'LIB001'}
)
if not p_created:
    profile.role = 'librarian'
    profile.save()

print("Librarian user created successfully.")
