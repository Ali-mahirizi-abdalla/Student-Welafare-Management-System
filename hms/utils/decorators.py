"""
Custom decorators for Student Welfare Management System (SWMS)
Provides reusable decorators for access control and functionality
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .helpers import is_user_admin, is_user_student


def student_required(view_func):
    """
    Decorator to ensure user has a student profile
    Redirects to login if not authenticated, raises 403 if not a student
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in to access this page.")
            return redirect('hms:login')
        
        if not is_user_student(request.user):
            raise PermissionDenied("This page is only accessible to students.")
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def admin_required(view_func):
    """
    Decorator to ensure user is admin/staff
    Redirects to login if not authenticated, raises 403 if not admin
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in to access this page.")
            return redirect('hms:login')
        
        if not is_user_admin(request.user):
            raise PermissionDenied("This page is only accessible to administrators.")
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def warden_or_admin_required(view_func):
    """
    Decorator to ensure user is warden or admin
    Redirects to login if not authenticated, raises 403 if insufficient permissions
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in to access this page.")
            return redirect('hms:login')
        
        is_admin = is_user_admin(request.user)
        is_warden = (is_user_student(request.user) and 
                    request.user.student_profile.is_warden)
        
        if not (is_admin or is_warden):
            raise PermissionDenied("This page is only accessible to wardens and administrators.")
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def ajax_required(view_func):
    """
    Decorator to ensure request is AJAX/XMLHttpRequest
    Returns 400 Bad Request if not AJAX
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.http import HttpResponseBadRequest
            return HttpResponseBadRequest("This endpoint only accepts AJAX requests.")
        
        return view_func(request, *args, **kwargs)
    
    return wrapper
