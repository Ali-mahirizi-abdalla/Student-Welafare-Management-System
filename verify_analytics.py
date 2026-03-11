import os
import django
from django.utils import timezone
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'swms.settings')
django.setup()

from rest_framework.test import APIRequestFactory
from hms.api.analytics import ActivityAnalyticsView

factory = APIRequestFactory()
view = ActivityAnalyticsView.as_view()

print("--- Testing Weekly (Rolling 7 Days) ---")
request_w = factory.get('/api/analytics/activity/', {'range': 'weekly'})
response_w = view(request_w)
print(f"Status: {response_w.status_code}")
print(f"Labels: {response_w.data.get('labels')}")
print(f"KPI Total: {response_w.data.get('kpis').get('total_activity')}")

print("\n--- Testing Monthly (Rolling 30 Days) ---")
request_m = factory.get('/api/analytics/activity/', {'range': 'monthly'})
response_m = view(request_m)
print(f"Status: {response_m.status_code}")
print(f"Labels length: {len(response_m.data.get('labels'))}")
print(f"Data Points per dataset: {len(response_m.data.get('datasets').get('registrations'))}")
