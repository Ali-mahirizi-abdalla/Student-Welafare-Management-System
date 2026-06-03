import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'swms.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

u = User.objects.filter(username='test_admin').first()
if not u:
    print("User 'test_admin' not found.")
    sys.exit(1)

c = Client(raise_request_exception=False, HTTP_HOST='localhost')
c.force_login(u)
r = c.get('/manage/permissions/matrix/')

if r.status_code == 500:
    content = r.content.decode('utf-8', errors='replace')
    import re
    m = re.search(r'<pre class="exception_value">(.*?)</pre>', content, re.DOTALL)
    if m:
        print('EXCEPTION:', m.group(1).strip())
    else:
        print('Could not find exception value.')
        
    m2 = re.search(r'<title>(.*?)</title>', content, re.DOTALL)
    if m2:
        print('TITLE:', m2.group(1).strip())
else:
    print(f"Status is {r.status_code}, no 500 error!")
