import os
import django
from django.utils import timezone
from datetime import timedelta
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'swms.settings')
django.setup()

from subscription.models import Subscription

def create_initial_subscription():
    print(" Creating initial subscription record...")
    
    # Check if any active subscription already exists
    if Subscription.objects.filter(status='active').exists():
        print(" Active subscription already exists.")
        return

    # Create a subscription starting March 1, 2026
    start_date = timezone.datetime(2026, 3, 1).date()
    end_date = start_date + timedelta(days=30)
    
    Subscription.objects.create(
        plan='monthly',
        status='active',
        start_date=start_date,
        end_date=end_date,
        amount_paid=3000.00,
        payment_date=timezone.now(),
        transaction_id="INIT-SUB-2026"
    )
    
    print(f" Subscription created successfully!")
    print(f" Start Date: {start_date}")
    print(f" End Date: {end_date}")
    print(f" Status: Active")

if __name__ == '__main__':
    create_initial_subscription()
