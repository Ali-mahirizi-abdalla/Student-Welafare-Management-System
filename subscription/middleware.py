import datetime
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from .models import Subscription

class SubscriptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        # 1. Exempt static/media/admin immediately
        if path.startswith('/static/') or path.startswith('/media/') or path.startswith('/admin/'):
            return self.get_response(request)

        # 2. Check date (March 1, 2026)
        cutoff_date = datetime.date(2026, 3, 1)
        today = timezone.now().date()
        
        # If before cutoff, allow everything
        if today < cutoff_date:
            return self.get_response(request)

        # 3. Exempt subscription pages to prevent redirect loops
        if path.startswith('/subscription/'):
            return self.get_response(request)

        # 4. Exempt Login/Logout/Accounts
        # We try to get the login URL safely
        exempt_paths = ['/accounts/', '/login/', '/logout/']
        try:
            # Try to reverse typical login URLs if they exist
            exempt_paths.append(reverse('hms:login'))
        except Exception:
            pass # URL conf might not be loaded yet or names don't exist
            
        if any(path.startswith(p) or path == p for p in exempt_paths):
            return self.get_response(request)

        # 5. Check for valid Active Subscription
        # We look for ANY active subscription that is satisfied
        has_active_subscription = Subscription.objects.filter(
            status='active',
            end_date__gte=today
        ).exists()

        if has_active_subscription:
            return self.get_response(request)
        
        # 6. Redirect if locked
        return redirect('subscription:index')
