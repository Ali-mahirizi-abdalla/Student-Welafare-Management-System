from django.shortcuts import redirect
from django.urls import reverse, NoReverseMatch
from django.core.cache import cache
from django.utils import timezone
import threading
from .models import AdminSubscription

# Thread-local storage to pass request info to signals
_thread_locals = threading.local()

def get_current_request():
    return getattr(_thread_locals, 'request', None)

class AuditMiddleware:
    """
    Middleware to capture request details (User, IP) for Audit Logging.
    Stores request in thread-local storage for access in signals.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_locals.request = request
        response = self.get_response(request)
        
        # Cleanup
        if hasattr(_thread_locals, 'request'):
            del _thread_locals.request
            
        return response

class PresenceMiddleware:
    """
    Middleware to track user 'online' status using Django Cache.
    A user is considered online if they've made a request within the last 5 minutes.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Mark user as active by storing a timestamp in cache
            # Key: 'seen_[user_id]', Value: 'online', Expiry: 300 seconds (5 min)
            cache_key = f'seen_{request.user.id}'
            cache.set(cache_key, 'online', 300)
            
        response = self.get_response(request)
        return response

class SubscriptionLockMiddleware:
    """
    Middleware to lock the system if the admin subscription has expired.
    Whitelists logic for payment, login, and static files.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Scheduled Activation Check: Features start May 1st, 2026
        activation_date = timezone.datetime(2026, 5, 1, tzinfo=timezone.get_current_timezone())
        if timezone.now() < activation_date:
            return self.get_response(request)

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

        # Check subscription status
        active_sub = AdminSubscription.objects.filter(status='Active', expiry_date__gt=timezone.now()).exists()

        if not active_sub:
            # If the user is staff, redirect to payment page
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
