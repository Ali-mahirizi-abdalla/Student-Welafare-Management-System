from django.test import RequestFactory
from django.contrib.auth.models import User
from hms.decorators import role_required
from django.http import HttpResponse

@role_required(allowed_roles=['dean_of_students'])
def dummy_view(request):
    return HttpResponse("SUCCESS")

user = User.objects.create(username='no_profile_test2')
factory = RequestFactory()
request = factory.get('/')
request.user = user

try:
    response = dummy_view(request)
    print(f"Response: {response.content}")
except Exception as e:
    print(f"CRASHED: {type(e).__name__}: {str(e)}")

user.delete()
