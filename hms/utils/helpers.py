"""
Helper utility functions for Student Welfare Management System (SWMS)
Provides common reusable functions used across the application
"""
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta
import re


def get_user_role(user):
    """
    Determine the role of a user in the system
    
    Args:
        user: Django User object
        
    Returns:
        str: User role ('admin', 'warden', 'student')
    """
    if user.is_superuser or user.is_staff:
        return 'admin'
    
    if hasattr(user, 'student_profile') and user.student_profile.is_warden:
        return 'warden'
    
    return'student'


def is_user_student(user):
    """Check if user has a student profile"""
    return hasattr(user, 'student_profile')


def is_user_admin(user):
    """Check if user is admin or staff"""
    return user.is_superuser or user.is_staff


def format_phone_number(phone):
    """
    Format phone number to Kenyan standard (254XXXXXXXXX)
    
    Args:
        phone: Raw phone number string
        
    Returns:
        str: Formatted phone number or original if invalid
    """
    # Remove any spaces, dashes, or parentheses
    phone = re.sub(r'[\s\-\(\)]', '', str(phone))
    
    # Handle different formats
    if phone.startswith('0'):
        phone = '254' + phone[1:]
    elif phone.startswith('+254'):
        phone = phone[1:]
    elif phone.startswith('254'):
        pass  # Already in correct format
    
    # Validate length (should be 12 digits: 254XXXXXXXXX)
    if len(phone) == 12 and phone.startswith('254'):
        return phone
    
    return phone  # Return as-is if we can't format


def get_client_ip(request):
    """
    Get the client's real IP address from request
    
    Args:
        request: Django request object
        
    Returns:
        str: IP address
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def is_within_timeframe(start_time, end_time, check_time=None):
    """
    Check if current time (or provided time) is within a timeframe
    
    Args:
        start_time: datetime.time object
        end_time: datetime.time object
        check_time: datetime.time object (defaults to current time)
        
    Returns:
        bool: True if within timeframe
    """
    if check_time is None:
        check_time = timezone.now().time()
    
    if start_time <= end_time:
        return start_time <= check_time <= end_time
    else:  # Crosses midnight
        return check_time >= start_time or check_time <= end_time


def get_academic_year():
    """
    Get current academic year string (e.g., "2025/2026")
    
    Returns:
        str: Academic year
    """
    today = timezone.now().date()
    if today.month >= 9:  # September onwards
        return f"{today.year}/{today.year + 1}"
    else:
        return f"{today.year - 1}/{today.year}"


def calculate_days_between(start_date, end_date):
    """
    Calculate number of days between two dates (inclusive)
    
    Args:
        start_date: datetime.date object
        end_date: datetime.date object
        
    Returns:
        int: Number of days
    """
    return (end_date - start_date).days + 1


def truncate_text(text, max_length=100, suffix='...'):
    """
    Truncate text to maximum length with suffix
    
    Args:
        text: String to truncate
        max_length: Maximum length
        suffix: String to append if truncated
        
    Returns:
        str: Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def add_success_message(request, message):
    """Helper to add success message"""
    messages.success(request, message)


def add_error_message(request, message):
    """Helper to add error message"""
    messages.error(request, message)


def add_warning_message(request, message):
    """Helper to add warning message"""
    messages.warning(request, message)


def add_info_message(request, message):
    """Helper to add info message"""
    messages.info(request, message)
