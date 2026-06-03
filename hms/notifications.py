"""
Notification Utilities for CampusCare
Supports Email and SMS notifications
"""
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """Unified notification service for email and SMS"""
    
    @staticmethod
    def send_email(to_email, subject, message, html_message=None):
        """Send email notification
        
        Args:
            to_email: Recipient email address (str or list)
            subject: Email subject
            message: Plain text message
            html_message: Optional HTML message
        
        Returns:
            bool: True if sent successfully, False otherwise
        """
        try:
            if isinstance(to_email, str):
                to_email = [to_email]
            
            if html_message:
                email = EmailMultiAlternatives(
                    subject=subject,
                    body=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=to_email
                )
                email.attach_alternative(html_message, "text/html")
                email.send(fail_silently=False)
            else:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=to_email,
                    fail_silently=False
                )
            
            logger.info(f"Email sent to {to_email}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    @staticmethod
    def send_sms(phone_number, message):
        """Send SMS via Africa's Talking"""
        import os
        try:
            username = os.environ.get('AFRICASTALKING_USERNAME', 'sandbox')
            api_key = os.getenv('AFRICASTALKING_API_KEY')
            if not api_key:
                logger.warning("[SMS SKIPPED] AFRICASTALKING_API_KEY not configured.")
                return False

            # Format phone: 07XX -> +254XX
            phone = phone_number.strip().replace(' ', '').replace('-', '') if phone_number else None
            if not phone:
                return False
            if phone.startswith('0') and len(phone) == 10:
                phone = '+254' + phone[1:]
            elif phone.startswith('254') and not phone.startswith('+'):
                phone = '+' + phone

            import africastalking
            africastalking.initialize(username, api_key)
            sms = africastalking.SMS
            sender_id = os.environ.get('AFRICASTALKING_SENDER_ID')
            if sender_id:
                response = sms.send(message, [phone], sender_id)
            else:
                response = sms.send(message, [phone])
            logger.info(f"[SMS SENT] {phone}: {response}")
            return True
        except Exception as e:
            logger.error(f"[SMS ERROR] {phone_number}: {str(e)}")
            return False


# ==================== NOTIFICATION TEMPLATES ====================

def notify_deferment_request_submitted(deferment_request):
    """Notify admin when a new deferment request is submitted"""
    
    admin_email = getattr(settings, 'ADMIN_EMAIL', None)
    if not admin_email:
        return False
    
    subject = f"🏠 New Deferment Request from {deferment_request.student.user.get_full_name()}"
    message = f"""
A new deferment request has been submitted:

Student: {deferment_request.student.user.get_full_name()}
University ID: {deferment_request.student.university_id}
Deferment Type: {deferment_request.get_deferment_type_display()}
Duration: {deferment_request.start_date} to {deferment_request.end_date}
Reason: {deferment_request.reason}

Please review this request in the admin dashboard.
    """
    
    return NotificationService.send_email(admin_email, subject, message)


def notify_deferment_status(deferment_request):
    """Notify student when their deferment request status changes"""
    student_email = deferment_request.student.user.email
    student_phone = deferment_request.student.phone
    
    status_display = deferment_request.get_status_display()
    
    if deferment_request.status == 'approved':
        subject = "✅ Deferment Request Approved"
        headers = "Your deferment request has been APPROVED!"
        sms_body = f"CampusCare: Your deferment from {deferment_request.start_date} to {deferment_request.end_date} is APPROVED."
    elif deferment_request.status == 'rejected':
        subject = "❌ Deferment Request Rejected"
        headers = "Unfortunately, your deferment request has been rejected."
        sms_body = "CampusCare: Your deferment request has been REJECTED. Check your email for details."
    elif deferment_request.status == 'under_review':
        subject = "👀 Deferment Request Under Review"
        headers = "Your deferment application is now under review."
        sms_body = "CampusCare: Your deferment application is being reviewed. You will be notified of the decision soon."
    elif deferment_request.status == 'resumed':
        subject = "🎓 Studies Resumed"
        headers = "Welcome back! Your status has been updated to Resumed Studies."
        sms_body = "CampusCare: Welcome back! Your student status has been updated to Resumed Studies."
    else:
        # Pending or other
        subject = f"📄 Deferment Status: {status_display}"
        headers = f"Your deferment request status is now: {status_display}"
        sms_body = f"CampusCare: Your deferment status is now {status_display}."

    message = f"""
Dear {deferment_request.student.user.first_name},

{headers}

Details:
- Type: {deferment_request.get_deferment_type_display()}
- Duration: {deferment_request.start_date} to {deferment_request.end_date}

Admin Notes: {deferment_request.admin_response or 'None'}

Best regards,
Student Welfare Management System
    """
    
    # Send email
    email_sent = NotificationService.send_email(student_email, subject, message)
    
    # Send SMS if phone available and user has opted in
    sms_sent = False
    if student_phone:
        try:
            sms_enabled = deferment_request.student.user.notification_preferences.sms_notifications
        except Exception:
            sms_enabled = False
        if sms_enabled:
            sms_sent = NotificationService.send_sms(student_phone, sms_body)
    
    return email_sent or sms_sent

# Aliases for backward compatibility
notify_leave_request_submitted = notify_deferment_request_submitted
notify_leave_request_status = notify_deferment_status


def _sms_enabled_for_user(user):
    """Return True if user has enabled SMS notifications in their preferences."""
    try:
        return user.notification_preferences.sms_notifications
    except Exception:
        return False


def notify_welcome(student):
    """Send welcome SMS to a newly registered student"""
    user = student.user
    if not _sms_enabled_for_user(user):
        return False
    msg = (
        f"Welcome to Campus Care, {user.first_name}! "
        f"Your account is active. Login: https://www.campus-care.co.ke "
        f"ID: {student.university_id or 'Pending'}"
    )
    return NotificationService.send_sms(student.phone, msg)


def notify_emergency_sms(phone_numbers, alert_message):
    """Broadcast an emergency alert SMS to a list of phone numbers"""
    import os
    try:
        username = os.environ.get('AFRICASTALKING_USERNAME', 'sandbox')
        api_key = os.getenv('AFRICASTALKING_API_KEY')
        if not api_key:
            logger.warning("[EMERGENCY SMS SKIPPED] API key not configured.")
            return False
        import africastalking
        africastalking.initialize(username, api_key)
        sms = africastalking.SMS
        sender_id = os.environ.get('AFRICASTALKING_SENDER_ID')
        phones = [p.strip() for p in phone_numbers if p]
        full_msg = f"🚨 CAMPUS CARE EMERGENCY: {alert_message}. Follow safety protocols."
        if sender_id:
            response = sms.send(full_msg, phones, sender_id)
        else:
            response = sms.send(full_msg, phones)
        logger.info(f"[EMERGENCY SMS]: {response}")
        return True
    except Exception as e:
        logger.error(f"[EMERGENCY SMS ERROR] {e}")
        return False


def notify_maintenance_status_update(maintenance_request):
    """Notify student when their maintenance request status changes"""
    student_email = maintenance_request.student.user.email
    student_phone = maintenance_request.student.phone
    
    status_emoji = {
        'pending': '🟡',
        'in_progress': '🔵',
        'resolved': '🟢'
    }
    
    emoji = status_emoji.get(maintenance_request.status, '📢')
    
    subject = f"{emoji} Maintenance Request Update: {maintenance_request.title}"
    message = f"""
Dear {maintenance_request.student.user.first_name},

Your maintenance request has been updated:

Title: {maintenance_request.title}
New Status: {maintenance_request.get_status_display()}
Priority: {maintenance_request.get_priority_display()}

Description: {maintenance_request.description}

Thank you for your patience.

Best regards,
Student Welfare Management System
    """
    
    sms_message = f"CampusCare: Your maintenance request '{maintenance_request.title}' is now {maintenance_request.get_status_display()}."
    
    # Send email
    email_sent = NotificationService.send_email(student_email, subject, message)
    
    # Send SMS if phone available
    sms_sent = False
    if student_phone:
        sms_sent = NotificationService.send_sms(student_phone, sms_message)
    
    return email_sent or sms_sent


def notify_new_announcement(announcement):
    """Notify all students about a new announcement"""
    from .models import Student
    
    students = Student.objects.select_related('user').all()
    
    priority_emoji = {
        'low': 'ℹ️',
        'normal': '📢',
        'high': '⚠️',
        'urgent': '🚨'
    }
    
    emoji = priority_emoji.get(announcement.priority, '📢')
    
    subject = f"{emoji} {announcement.title}"
    message = f"""
Dear Student,

{announcement.content}

---
This is an official announcement from the Student Welfare Management System.
Priority: {announcement.get_priority_display()}
Posted: {announcement.created_at.strftime('%B %d, %Y at %H:%M')}
    """
    
    # Only send SMS for high/urgent announcements
    send_sms_notification = announcement.priority in ['high', 'urgent']
    sms_message = f"CampusCare ({announcement.get_priority_display()}): {announcement.title[:100]}"
    
    success_count = 0
    for student in students:
        if student.user.email:
            if NotificationService.send_email(student.user.email, subject, message):
                success_count += 1
        
        if send_sms_notification and student.phone:
            NotificationService.send_sms(student.phone, sms_message)
    
    return success_count


def notify_meal_reminder(student, meal_date):
    """Send meal confirmation reminder to a student"""
    subject = f"🍽️ Reminder: Confirm Your Meals for {meal_date.strftime('%B %d')}"
    message = f"""
Dear {student.user.first_name},

This is a friendly reminder to confirm your meal preferences for {meal_date.strftime('%A, %B %d, %Y')}.

Please log in to the Student Welfare Management System and confirm your meals before 8:00 AM.

Best regards,
Student Welfare Management System
    """
    
    sms_message = f"CampusCare: Please confirm your meals for {meal_date.strftime('%b %d')} before 8 AM."
    
    email_sent = NotificationService.send_email(student.user.email, subject, message)
    
    if student.phone:
        NotificationService.send_sms(student.phone, sms_message)
    
    return email_sent


def send_bulk_meal_reminders():
    """Send reminders to all students who haven't confirmed meals for tomorrow"""
    from .models import Student, Meal
    from datetime import date, timedelta
    
    tomorrow = date.today() + timedelta(days=1)
    
    # Get students who haven't confirmed meals
    confirmed_ids = Meal.objects.filter(date=tomorrow).values_list('student_id', flat=True)
    unconfirmed_students = Student.objects.exclude(id__in=confirmed_ids)
    
    success_count = 0
    for student in unconfirmed_students:
        if notify_meal_reminder(student, tomorrow):
            success_count += 1
    
    return success_count, unconfirmed_students.count()
