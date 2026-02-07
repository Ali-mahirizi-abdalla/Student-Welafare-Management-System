from django.db.models.signals import post_save, post_delete
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from .models import AuditLog, Student, Meal, Announcement, MaintenanceRequest
from .middleware import get_current_request
import json

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    AuditLog.objects.create(
        user=user,
        action='LOGIN',
        model_name='User',
        object_id=str(user.id),
        object_repr=user.username,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    if user:
        AuditLog.objects.create(
            user=user,
            action='LOGOUT',
            model_name='User',
            object_id=str(user.id),
            object_repr=user.username,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )

# List of models to track
tracked_models = [Student, Meal, Announcement, MaintenanceRequest]

@receiver(post_save, sender=User)
def create_student_profile(sender, instance, created, **kwargs):
    """Automatically create a Student profile for new users."""
    if created:
        Student.objects.get_or_create(user=instance)

@receiver(post_save, sender=Student)
@receiver(post_save, sender=Meal)
@receiver(post_save, sender=Announcement)
@receiver(post_save, sender=MaintenanceRequest)
def log_create_update(sender, instance, created, **kwargs):
    request = get_current_request()
    user = request.user if (request and request.user.is_authenticated) else None
    
    # Avoid logging if no user is context (e.g. system tasks) or if it's the AuditLog itself
    if sender == AuditLog:
        return

    action = 'CREATE' if created else 'UPDATE'
    
    # Basic diff logic could go here, but for now we just log the event
    details = ""
    if not created:
        details = "Record updated" # Future: Implement field tracking

    AuditLog.objects.create(
        user=user,
        action=action,
        model_name=sender.__name__,
        object_id=str(instance.pk),
        object_repr=str(instance),
        details=details,
        ip_address=get_client_ip(request) if request else None,
        user_agent=request.META.get('HTTP_USER_AGENT', '') if request else None
    )

@receiver(post_delete, sender=Student)
@receiver(post_delete, sender=Meal)
@receiver(post_delete, sender=Announcement)
@receiver(post_delete, sender=MaintenanceRequest)
def log_delete(sender, instance, **kwargs):
    request = get_current_request()
    user = request.user if (request and request.user.is_authenticated) else None

    AuditLog.objects.create(
        user=user,
        action='DELETE',
        model_name=sender.__name__,
        object_id=str(instance.pk),
        object_repr=str(instance),
        ip_address=get_client_ip(request) if request else None,
        user_agent=request.META.get('HTTP_USER_AGENT', '') if request else None
    )
