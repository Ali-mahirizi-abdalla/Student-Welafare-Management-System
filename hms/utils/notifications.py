import os
import africastalking
from django.conf import settings


def get_at_client():
    """Initialize Africa's Talking lazily"""
    username = os.environ.get('AFRICASTALKING_USERNAME', 'sandbox')
    api_key = os.environ.get('AFRICASTALKING_API_KEY')
    if not api_key:
        return None
    africastalking.initialize(username, api_key)
    return africastalking


def format_phone(phone):
    """Convert phone number to international format (+254...)"""
    if not phone:
        return None
    phone = phone.strip().replace(' ', '').replace('-', '')
    if phone.startswith('0') and len(phone) == 10:
        return '+254' + phone[1:]
    if phone.startswith('254') and not phone.startswith('+'):
        return '+' + phone
    return phone


def send_sms(phone_number, message):
    """Send an SMS via Africa's Talking"""
    at = get_at_client()
    if not at:
        print(f"[SMS SKIPPED] Africa's Talking not configured. Message: {message}")
        return False

    phone = format_phone(phone_number)
    if not phone:
        print("[SMS SKIPPED] No phone number provided.")
        return False

    sms = at.SMS
    sender_id = os.environ.get('AFRICASTALKING_SENDER_ID')
    try:
        if sender_id:
            response = sms.send(message, [phone], sender_id)
        else:
            response = sms.send(message, [phone])
        print(f"[SMS SENT] {phone}: {response}")
        return True
    except Exception as e:
        print(f"[SMS ERROR] {e}")
        return False


def send_whatsapp(phone_number, message):
    """Placeholder for WhatsApp — logs message until AT WhatsApp is provisioned"""
    phone = format_phone(phone_number)
    print(f"[WHATSAPP] To {phone}: {message}")
    return True


# ─── Notification helpers ────────────────────────────────────────────────────

def notify_welcome(user, student):
    """Send welcome SMS after student registration"""
    if not _should_send(user, 'sms'):
        return
    msg = (
        f"Welcome to Campus Care, {user.first_name}!\n"
        f"Your account is ready. Login at: https://www.campus-care.co.ke\n"
        f"Student ID: {student.university_id or 'Pending'}"
    )
    send_sms(student.phone, msg)


def notify_deferment_decision(user, student, status, dates=''):
    """Notify student of deferment approval or rejection"""
    if not _should_send(user, 'sms'):
        return
    if status == 'approved':
        msg = (
            f"Campus Care: Your deferment request has been APPROVED"
            + (f" for {dates}." if dates else ".")
            + " Check the portal for details."
        )
    else:
        msg = (
            "Campus Care: Your deferment request has been REJECTED. "
            "Please contact the welfare office for assistance."
        )
    send_sms(student.phone, msg)


def notify_payment_confirmed(user, student, amount, receipt):
    """Notify student of payment receipt"""
    if not _should_send(user, 'sms'):
        return
    msg = (
        f"Campus Care: Payment of KES {amount} received successfully.\n"
        f"Receipt No: {receipt}\n"
        f"Thank you!"
    )
    send_sms(student.phone, msg)


def notify_appointment_reminder(user, student, appointment_date, appointment_time, service_type):
    """Remind student of upcoming health appointment"""
    if not _should_send(user, 'sms'):
        return
    msg = (
        f"Campus Care Reminder: You have a {service_type} appointment "
        f"on {appointment_date} at {appointment_time}. "
        f"Please arrive 10 minutes early."
    )
    send_sms(student.phone, msg)


def notify_emergency(phone_numbers, message):
    """Send emergency broadcast SMS to a list of phone numbers"""
    at = get_at_client()
    if not at:
        print(f"[EMERGENCY SMS SKIPPED] Not configured.")
        return False
    phones = [format_phone(p) for p in phone_numbers if p]
    if not phones:
        return False
    sms = at.SMS
    sender_id = os.environ.get('AFRICASTALKING_SENDER_ID')
    try:
        full_msg = f"🚨 CAMPUS CARE EMERGENCY: {message}. Follow safety protocols immediately."
        if sender_id:
            response = sms.send(full_msg, phones, sender_id)
        else:
            response = sms.send(full_msg, phones)
        print(f"[EMERGENCY SMS SENT]: {response}")
        return True
    except Exception as e:
        print(f"[EMERGENCY SMS ERROR] {e}")
        return False


def notify_staff_invitation(phone_number, role_display, invite_url):
    """Notify a staff member of their invitation via SMS"""
    msg = (
        f"Campus Care: You have been invited to join as {role_display}.\n"
        f"Register here: {invite_url}"
    )
    send_sms(phone_number, msg)


# ─── Internal helper ─────────────────────────────────────────────────────────

def _should_send(user, channel):
    """Check if user has opted in to a notification channel"""
    try:
        prefs = user.notification_preferences
        if channel == 'sms':
            return prefs.sms_notifications
        if channel == 'whatsapp':
            return prefs.whatsapp_notifications
        if channel == 'email':
            return prefs.email_notifications
    except Exception:
        pass  # If no prefs set, default to False for SMS/WhatsApp
    return False
