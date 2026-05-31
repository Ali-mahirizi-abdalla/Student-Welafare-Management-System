from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from functools import wraps

def role_required(allowed_roles=[]):
    """
    Decorator to restrict access based on StaffProfile.role (the model key).
    Also checks Django Groups for backward compatibility.
    Superusers always bypass.
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

            # 2. PRIMARY: Check StaffProfile.role (the actual model key e.g. 'super_admin', 'warden')
            staff_profile = getattr(request.user, 'staff_profile', None)
            if staff_profile and staff_profile.role in allowed_roles:
                return view_func(request, *args, **kwargs)

            # 3. SECONDARY: Check Django Groups (backward compatibility)
            user_groups = request.user.groups.values_list('name', flat=True)
            if any(role in user_groups for role in allowed_roles):
                return view_func(request, *args, **kwargs)

            raise PermissionDenied(f"Access restricted to: {', '.join(allowed_roles)}")

        return _wrapped_view
    return decorator


# ─────────────────────────────────────────────────────────
# Convenience shortcut decorators using actual model keys
# ─────────────────────────────────────────────────────────

def super_admin_required(view_func):
    return role_required(allowed_roles=['super_admin', 'Super Admin', 'SUPER_ADMIN'])(view_func)

# Backward-compatible alias - used in existing views
def admin_only(view_func):
    """Super Admin or system superusers only"""
    return role_required(allowed_roles=[
        'super_admin', 'Super Admin', 'SUPER_ADMIN',
        'vice_chancellor', 'deputy_vice_chancellor',
        'register_admin',
    ])(view_func)

def welfare_officer_required(view_func):
    return role_required(allowed_roles=[
        'super_admin', 'dean_of_students', 'support_agent',
        # legacy names
        'Welfare Officer', 'WELFARE_OFFICER', 'SUPER_ADMIN',
    ])(view_func)

def hostel_manager_required(view_func):
    return role_required(allowed_roles=[
        'super_admin', 'warden',
        # legacy names
        'Hostel Manager', 'HOSTEL_MANAGER', 'SUPER_ADMIN',
    ])(view_func)

def kitchen_manager_required(view_func):
    return role_required(allowed_roles=[
        'super_admin', 'health_manager',
        # legacy names
        'Kitchen Manager', 'KITCHEN_MANAGER', 'SUPER_ADMIN',
    ])(view_func)

def security_required(view_func):
    return role_required(allowed_roles=[
        'super_admin', 'security_officer', 'emergency_coord',
        # legacy names
        'Security', 'SECURITY_OFFICER', 'EMERGENCY_COORDINATOR', 'SUPER_ADMIN',
    ])(view_func)

def student_required(view_func):
    def check_student(user):
        return hasattr(user, 'student_profile') or user.is_superuser
    return user_passes_test(check_student)(view_func)

def staff_only(view_func):
    """Any staff member (non-student)"""
    def check_staff(user):
        return user.is_staff or hasattr(user, 'staff_profile') or user.is_superuser
    return user_passes_test(check_staff)(view_func)
