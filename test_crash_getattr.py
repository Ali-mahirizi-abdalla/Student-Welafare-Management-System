from django.contrib.auth.models import User
import traceback

print("Testing getattr on related object...")
user = User.objects.create(username='no_profile_test')

try:
    profile = getattr(user, 'staff_profile', None)
    print(f"Profile is: {profile}")
except Exception as e:
    print(f"CRASHED: {type(e).__name__}: {str(e)}")

user.delete()
