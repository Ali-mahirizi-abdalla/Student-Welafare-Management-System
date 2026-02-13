
import os
import django
from django.test import RequestFactory
from django.contrib.auth.models import User
from unittest.mock import patch

def verify():
    from hms.models import StaffProfile
    from hms.views import dashboard_admin
    
    rf = RequestFactory()
    
    # Mock render to capture context
    with patch('hms.views.render') as mock_render:
        # 1. Test Superadmin
        print("Testing Superadmin Visibility...")
        super_user = User.objects.filter(is_superuser=True).first()
        if not super_user:
            super_user = User.objects.create_superuser('temp_super', 'admin@test.com', 'pass')
            
        request = rf.get('/manage/dashboard/')
        request.user = super_user
        
        dashboard_admin(request)
        context = mock_render.call_args[0][2]
        print(f"  is_superadmin: {context.get('is_superadmin')}")
        print(f"  staff_role: {context.get('staff_role')}")
        
        # 2. Test Staff with role
        print("\nTesting Staff (DEFERMENT) Visibility...")
        staff_user = User.objects.filter(staff_profile__role='DEFERMENT').first()
        if staff_user:
            request.user = staff_user
            dashboard_admin(request)
            context = mock_render.call_args[0][2]
            print(f"  is_superadmin: {context.get('is_superadmin')}")
            print(f"  staff_role: {context.get('staff_role')}")
        else:
            print("  Skipping: No DEFERMENT staff found.")

if __name__ == "__main__":
    verify()
