from django.test import Client
from django.contrib.auth.models import User
import traceback

try:
    user = User.objects.filter(staff_profile__role='dean_of_students').first()
    print(f"Testing with user: {user.username}")
    client = Client(HTTP_HOST='localhost')
    client.force_login(user)
    
    response = client.get('/staff-dashboard/', follow=True)
    print(f"Final URL: {response.request.get('PATH_INFO')}")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 500:
        print("CRASHED!")
        print(response.content.decode())
    elif response.status_code >= 400:
        print(f"ERROR: {response.status_code}")
        print(response.content.decode()[:500])
    else:
        print("SUCCESS")
except Exception as e:
    print("EXCEPTION:")
    traceback.print_exc()
