from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from functools import wraps

def role_required(allowed_roles=[], allowed_categories=[]):
    """
    Decorator to restrict access to users in specific groups (roles) or categories.
    Usage: @role_required(allowed_roles=['Admin'], allowed_categories=['EXECUTIVE'])
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                from django.contrib.auth.views import redirect_to_login
                return redirect_to_login(request.get_full_path(), login_url='hms:login')
            
            # 1. Superuser always bypasses
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            # 2. Check if user is in any specifically allowed legacy groups
            user_groups = request.user.groups.values_list('name', flat=True)
            if allowed_roles:
                if any(role in user_groups for role in allowed_roles):
                    return view_func(request, *args, **kwargs)
            
            # 3. Check StaffProfile role and category (Strict departmental isolation)
            staff_profile = getattr(request.user, 'staff_profile', None)
            if staff_profile:
                # If specific roles are allowed (legacy/specific)
                if allowed_roles and staff_profile.role in allowed_roles:
                    return view_func(request, *args, **kwargs)
                
                # If specific categories are allowed (Modern/Strict)
                if allowed_categories:
                    user_category = staff_profile.get_category()
                    if user_category in allowed_categories:
                        return view_func(request, *args, **kwargs)
                    
                    # Special check: EXECUTIVE category can access almost everything
                    if user_category == 'EXECUTIVE':
                        return view_func(request, *args, **kwargs)
            
            # Use request objects to log permission denied in future if needed
            raise PermissionDenied("You do not have permission to access this resource. This feature is restricted to specific departments.")
            
        return _wrapped_view
    return decorator


def admin_only(view_func):
    """Strictly for system admins or executive staff"""
    return role_required(allowed_categories=['EXECUTIVE'])(view_func)

def staff_only(view_func):
    """Any staff member (non-student)"""
    def check_staff(user):
        return user.is_staff or hasattr(user, 'staff_profile')
    return user_passes_test(check_staff)(view_func)
