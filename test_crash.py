from django.test import RequestFactory
from hms.views import dashboard_redirect
from django.contrib.auth.models import User
import traceback

user = User.objects.filter(staff_profile__role='dean_of_students').first()
if not user:
    user = User.objects.filter(is_superuser=True).first()

print(f"Testing dashboard_redirect with user: {user}")

factory = RequestFactory()
request = factory.get('/staff-dashboard/')
request.user = user

try:
    response = dashboard_redirect(request)
    print(f"Redirected to: {response.url}")
    print("SUCCESS")
except Exception as e:
    print("CRASHED")
    traceback.print_exc()
