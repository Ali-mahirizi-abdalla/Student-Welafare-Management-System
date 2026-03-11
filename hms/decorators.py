from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from functools import wraps

def role_required(allowed_roles=[]):
    """
    Decorator to restrict access to users in specific groups (roles).
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

            # 2. Check if user is in any specifically allowed groups
            user_groups = request.user.groups.values_list('name', flat=True)
            if allowed_roles:
                if any(role in user_groups for role in allowed_roles):
                    return view_func(request, *args, **kwargs)
            
            # 3. Check StaffProfile role for secondary verification
            staff_profile = getattr(request.user, 'staff_profile', None)
            if staff_profile and staff_profile.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            
            raise PermissionDenied(f"Access restricted to: {', '.join(allowed_roles)}")
            
        return _wrapped_view
    return decorator

def super_admin_required(view_func):
    return role_required(allowed_roles=['Super Admin'])(view_func)

# Backward-compatible alias - used in existing views
def admin_only(view_func):
    """Strictly for Super Admin or system superusers"""
    return role_required(allowed_roles=['Super Admin'])(view_func)

def welfare_officer_required(view_func):
    return role_required(allowed_roles=['Welfare Officer', 'Super Admin'])(view_func)

def hostel_manager_required(view_func):
    return role_required(allowed_roles=['Hostel Manager', 'Super Admin'])(view_func)

def kitchen_manager_required(view_func):
    return role_required(allowed_roles=['Kitchen Manager', 'Super Admin'])(view_func)

def security_required(view_func):
    return role_required(allowed_roles=['Security', 'Super Admin'])(view_func)

def student_required(view_func):
    def check_student(user):
        return hasattr(user, 'student_profile') or user.is_superuser
    return user_passes_test(check_student)(view_func)

def staff_only(view_func):
    """Any staff member (non-student)"""
    def check_staff(user):
        return user.is_staff or hasattr(user, 'staff_profile') or user.is_superuser
    return user_passes_test(check_staff)(view_func)
