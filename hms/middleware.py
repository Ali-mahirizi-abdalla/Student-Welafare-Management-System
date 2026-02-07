from django.core.cache import cache
from django.utils import timezone
import threading

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
