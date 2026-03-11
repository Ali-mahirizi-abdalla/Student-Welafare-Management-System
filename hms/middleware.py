from django.shortcuts import redirect
from django.urls import reverse, NoReverseMatch
from django.utils import timezone
from .models import AdminSubscription

class SubscriptionLockMiddleware:
    """
    Middleware to lock the system if the admin subscription has expired.
    Whitelists logic for payment, login, and static files.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Static and media files are always whitelisted
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            return self.get_response(request)

        # Try to match whitelisted named URLs
        try:
            whitelisted_urls = [
                reverse('hms:login'),
                reverse('hms:logout'),
                reverse('hms:mpesa_callback'),
            ]
            # These might not be defined yet, so we handle NoReverseMatch
            try:
                whitelisted_urls.append(reverse('hms:admin_subscription_pay'))
                whitelisted_urls.append(reverse('hms:system_locked'))
                whitelisted_urls.append(reverse('hms:check_registration_status', kwargs={'checkout_id': 'dummy'}))
            except NoReverseMatch:
                pass
        except NoReverseMatch:
            whitelisted_urls = []

        if request.path in whitelisted_urls:
            return self.get_response(request)

        # Check subscription status (Cache would be better, but direct DB check for reliability during implementation)
        # We assume the first Active subscription is the valid one
        active_sub = AdminSubscription.objects.filter(status='Active', expiry_date__gt=timezone.now()).exists()

        if not active_sub:
            # If the user is staff, redirect to payment page
            # Otherwise redirect to system-locked page
            if request.user.is_authenticated and request.user.is_staff:
                try:
                    pay_url = reverse('hms:admin_subscription_pay')
                    if request.path != pay_url:
                        return redirect(pay_url)
                except NoReverseMatch:
                    pass
            else:
                try:
                    lock_url = reverse('hms:system_locked')
                    if request.path != lock_url:
                        return redirect(lock_url)
                except NoReverseMatch:
                    pass

        return self.get_response(request)
