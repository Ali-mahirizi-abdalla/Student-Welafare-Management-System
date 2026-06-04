from django.contrib.auth import get_user_model
User = get_user_model()
from hms.models import StaffProfile

user, created = User.objects.get_or_create(username='librarian', defaults={'email': 'lib@campus.com'})
user.is_staff = True
user.set_password('lib123')
user.save()

profile, p_created = StaffProfile.objects.get_or_create(user=user, defaults={'role': 'librarian', 'national_id': 'LIB001'})
if not p_created:
    profile.role = 'librarian'
    profile.save()
print("Librarian user created successfully.")
