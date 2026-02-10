from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from functools import wraps

def role_required(allowed_roles=[]):
    """
    Decorator to restrict access to users in specific groups (roles).
    Usage: @role_required(['Admin', 'Warden'])
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                from django.contrib.auth.views import redirect_to_login
                return redirect_to_login(request.get_full_path())
            
            # Superuser always bypasses
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            # Check if user is in any of the allowed groups
            user_groups = request.user.groups.values_list('name', flat=True)
            if any(role in user_groups for role in allowed_roles):
                return view_func(request, *args, **kwargs)
            
            # Check StaffProfile role
            staff_profile = getattr(request.user, 'staff_profile', None)
            if staff_profile and staff_profile.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            
            # Use request objects to log permission denied in future if needed
            raise PermissionDenied("You do not have permission to access this resource.")
            
        return _wrapped_view
    return decorator

def admin_only(view_func):
    return role_required(['Admin'])(view_func)
