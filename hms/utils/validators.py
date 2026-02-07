"""
Custom validators for Student Welfare Management System (SWMS)
Provides validation functions for forms and models
"""
from django.core.exceptions import ValidationError
from django.utils import timezone
import re


def validate_university_id(value):
    """
    Validate university ID format
    Should be alphanumeric, typically 6-20 characters
    """
    if not value:
        return
    
    if not re.match(r'^[A-Za-z0-9\-]+$', value):
        raise ValidationError(
            'University ID must contain only letters, numbers, and hyphens.'
        )
    
    if len(value) < 3 or len(value) > 20:
        raise ValidationError(
            'University ID must be between 3 and 20 characters.'
        )


def validate_phone_number(value):
    """
    Validate phone number format (Kenyan format)
    Accepts: 07XXXXXXXX, +254XXXXXXXXX, 254XXXXXXXXX
    """
    if not value:
        return
    
    # Remove spaces and common separators
    cleaned = re.sub(r'[\s\-\(\)]', '', str(value))
    
    # Check various valid formats
    valid_patterns = [
        r'^07\d{8}$',  # 07XXXXXXXX
        r'^01\d{8}$',  # 01XXXXXXXX
        r'^\+2547\d{8}$',  # +2547XXXXXXXX
        r'^\+2541\d{8}$',  # +2541XXXXXXXX
        r'^2547\d{8}$',  # 2547XXXXXXXX
        r'^2541\d{8}$',  # 2541XXXXXXXX
    ]
    
    if not any(re.match(pattern, cleaned) for pattern in valid_patterns):
        raise ValidationError(
            'Enter a valid phone number (e.g., 0712345678 or +254712345678).'
        )


def validate_file_size(file, max_size_mb=5):
    """
    Validate uploaded file size
    
    Args:
        file: UploadedFile object
        max_size_mb: Maximum size in megabytes
    """
    if file.size > max_size_mb * 1024 * 1024:
        raise ValidationError(
            f'File size must not exceed {max_size_mb}MB. Current size: {file.size / (1024 * 1024):.2f}MB'
        )


def validate_image_file(file):
    """
    Validate that uploaded file is an image
    """
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    file_extension = file.name.lower().split('.')[-1]
    
    if f'.{file_extension}' not in valid_extensions:
        raise ValidationError(
            f'Invalid file type. Allowed types: {", ".join(valid_extensions)}'
        )


def validate_document_file(file):
    """
    Validate that uploaded file is a document
    """
    valid_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.txt']
    file_extension = file.name.lower().split('.')[-1]
    
    if f'.{file_extension}' not in valid_extensions:
        raise ValidationError(
            f'Invalid file type. Allowed types: {", ".join(valid_extensions)}'
        )


def validate_date_not_past(value):
    """
    Validate that date is not in the past
    """
    if value < timezone.now().date():
        raise ValidationError('Date cannot be in the past.')


def validate_date_range(start_date, end_date):
    """
    Validate that end_date is after start_date
    """
    if start_date > end_date:
        raise ValidationError('End date must be after start date.')


def validate_room_number(value):
    """
    Validate room number format
    """
    if not value:
        return
    
    if not re.match(r'^[A-Za-z0-9\-]+$', value):
        raise ValidationError(
            'Room number must contain only letters, numbers, and hyphens.'
        )
    
    if len(value) > 10:
        raise ValidationError('Room number must not exceed 10 characters.')


def validate_amount(value):
    """
    Validate monetary amount
    """
    if value < 0:
        raise ValidationError('Amount cannot be negative.')
    
    if value > 1000000:  # 1 million limit
        raise ValidationError('Amount exceeds maximum allowed value.')
