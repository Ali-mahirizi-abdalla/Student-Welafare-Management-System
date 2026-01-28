from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, datetime

class Student(models.Model):
    """Extended profile for students"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    university_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    profile_image = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    timetable = models.FileField(upload_to='timetables/', blank=True, null=True)
    room_number = models.CharField(max_length=10, blank=True, null=True)
    HOSTEL_CHOICES = [
        ('Hostel 1', 'Hostel 1'),
        ('Hostel 2', 'Hostel 2'),
        ('Hostel 3', 'Hostel 3'),
        ('Hostel 4', 'Hostel 4'),
        ('Hostel 5', 'Hostel 5'),
        ('Hostel 6', 'Hostel 6'),
        ('Hostel 7', 'Hostel 7'),
    ]
    hostel = models.CharField(max_length=20, choices=HOSTEL_CHOICES, blank=True, null=True)
    is_warden = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.university_id})"

class Meal(models.Model):
    """Daily meal submission"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='meals')
    date = models.DateField(default=date.today)
    breakfast = models.BooleanField(default=False)
    early = models.BooleanField(default=False) # Early breakfast
    supper = models.BooleanField(default=False)
    away = models.BooleanField(default=False) # Check if marked away for this specific day
    submitted_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['student', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.student} - {self.date}"

class AwayPeriod(models.Model):
    """Periods when a student is away"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='away_periods')
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.start_date > self.end_date:
            raise ValidationError("End date must be after start date.")

    def __str__(self):
        return f"{self.student} Away: {self.start_date} to {self.end_date}"

class Activity(models.Model):
    """Weekly activities"""
    display_name = models.CharField(max_length=100)
    weekday = models.IntegerField(choices=[
        (0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'),
        (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')
    ])
    description = models.TextField(blank=True)
    time = models.TimeField(null=True, blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Activities"
        ordering = ['weekday', 'time']

    def __str__(self):
        return f"{self.get_weekday_display()} - {self.display_name}"

class Announcement(models.Model):
    """System announcements"""
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='announcements')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    priority = models.CharField(max_length=20, choices=[
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    ], default='normal')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class Document(models.Model):
    """Admin uploaded documents for students"""
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class Message(models.Model):
    """Chat messages between student and admin"""
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"From {self.sender} to {self.recipient}"


class MaintenanceRequest(models.Model):
    """Maintenance tickets submitted by students"""
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='maintenance_requests')
    title = models.CharField(max_length=200)
    description = models.TextField()
    photo = models.ImageField(upload_to='maintenance_photos/', blank=True, null=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.student} ({self.get_status_display()})"


class Room(models.Model):
    """Student room information"""
    ROOM_TYPES = [
        ('single', 'Single'),
        ('double', 'Double'),
        ('triple', 'Triple'),
        ('quad', 'Quad'),
    ]
    
    room_number = models.CharField(max_length=10, unique=True)
    floor = models.IntegerField()
    block = models.CharField(max_length=50, blank=True)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES, default='double')
    capacity = models.IntegerField(default=2)
    is_available = models.BooleanField(default=True)
    amenities = models.TextField(blank=True, help_text="List amenities (e.g., AC, attached bathroom)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['block', 'floor', 'room_number']
    
    def __str__(self):
        return f"Room {self.room_number} - {self.get_room_type_display()}"
    
    @property
    def current_occupancy(self):
        """Get current number of students in the room"""
        return self.assignments.filter(is_active=True).count()
    
    @property
    def available_beds(self):
        """Get number of available beds"""
        return self.capacity - self.current_occupancy


class RoomAssignment(models.Model):
    """Track room assignments for students"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='room_assignments')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='assignments')
    bed_number = models.IntegerField(null=True, blank=True)
    assigned_date = models.DateField(default=date.today)
    checkout_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-assigned_date']
    
    def __str__(self):
        return f"{self.student} - {self.room} (Bed {self.bed_number})"


class RoomChangeRequest(models.Model):
    """Student requests for room changes"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='room_change_requests')
    current_room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, related_name='change_requests_from')
    requested_room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True, related_name='change_requests_to')
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_room_changes')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student} - Room Change Request ({self.get_status_display()})"


class DefermentRequest(models.Model):
    """Student deferment applications for various reasons"""
    STATUS_CHOICES = [
        ('pending', 'Pending Application'),
        ('under_review', 'Sent for Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('resumed', 'Resumed Studies'),
    ]
    
    DEFERMENT_TYPES = [
        ('fee_challenges', 'Fee Challenges'),
        ('motherhood_fatherhood', 'Motherhood/Fatherhood'),
        ('gainful_employment', 'Pursuing Gainful Employment'),
        ('family_disruption', 'Disruption of Family'),
        ('moving_country', 'Moving Out of the Country'),
        ('natural_calamity', 'Natural Calamity'),
        ('political_calamity', 'Political Calamity'),
        ('program_challenges', 'Challenges in the Current Program'),
        ('other', 'Others (Please State)'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='leave_requests')
    deferment_type = models.CharField(max_length=30, choices=DEFERMENT_TYPES, help_text="Select the reason for deferment")
    other_reason_detail = models.TextField(blank=True, help_text="If 'Others', please provide details")
    start_date = models.DateField(help_text="Expected deferment start date")
    end_date = models.DateField(help_text="Expected deferment end date")
    reason = models.TextField(help_text="Detailed explanation of your deferment request")
    contact_during_deferment = models.CharField(max_length=15, blank=True, help_text="Phone number during deferment")
    supporting_documents = models.FileField(upload_to='deferment_docs/', blank=True, null=True, help_text="Upload supporting documents if any")
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True, help_text="Administrative notes and feedback")
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_leaves')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Deferment Request'
        verbose_name_plural = 'Deferment Requests'
        db_table = 'hms_leaverequest'  # Keep existing table name for compatibility
    
    def __str__(self):
        return f"{self.student} - Deferment ({self.get_deferment_type_display()})"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.start_date > self.end_date:
            raise ValidationError("End date must be after start date.")
        if self.deferment_type == 'other' and not self.other_reason_detail:
            raise ValidationError("Please provide details when selecting 'Others' as deferment type.")
    
    @property
    def duration_days(self):
        """Calculate deferment duration in days"""
        return (self.end_date - self.start_date).days + 1


# Keep LeaveRequest as an alias for backwards compatibility during migration
LeaveRequest = DefermentRequest


class Visitor(models.Model):
    """Visitor logbook for security"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='visitors')
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15, blank=True)
    id_number = models.CharField(max_length=50, blank=True, help_text="National ID or Passport Number")
    
    check_in_time = models.DateTimeField(default=timezone.now)
    check_out_time = models.DateTimeField(null=True, blank=True)
    purpose = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='registered_visitors')
    
    class Meta:
        ordering = ['-check_in_time']
    
    def __str__(self):
        return f"{self.name} visiting {self.student}"
    
    def check_out(self):
        self.check_out_time = timezone.now()
        self.is_active = False
        self.save()


class Event(models.Model):
    """Events and activities"""
    EVENT_CATEGORIES = [
        ('social', 'Social Event'),
        ('educational', 'Educational'),
        ('sports', 'Sports'),
        ('cultural', 'Cultural'),
        ('meeting', 'Meeting'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=EVENT_CATEGORIES, default='social')
    
    event_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField(null=True, blank=True)
    
    location = models.CharField(max_length=200)
    max_participants = models.IntegerField(null=True, blank=True, help_text="Leave blank for unlimited")
    
    image = models.ImageField(upload_to='event_images/', blank=True, null=True)
    is_mandatory = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    requires_rsvp = models.BooleanField(default=True)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_events')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-event_date', '-start_time']
    
    def __str__(self):
        return f"{self.title} - {self.event_date}"
    
    @property
    def rsvp_count(self):
        """Get number of students who have RSVPed"""
        return self.rsvps.filter(status='attending').count()
    
    @property
    def is_full(self):
        """Check if event has reached capacity"""
        if self.max_participants:
            return self.rsvp_count >= self.max_participants
        return False
    
    @property
    def is_past(self):
        """Check if event is in the past"""
        from datetime import datetime
        event_datetime = datetime.combine(self.event_date, self.start_time)
        return event_datetime < datetime.now()
    
    @property
    def spots_remaining(self):
        """Get number of spots remaining"""
        if self.max_participants:
            return max(0, self.max_participants - self.rsvp_count)
        return None


class EventRSVP(models.Model):
    """Student RSVP for events"""
    RSVP_STATUS = [
        ('attending', 'Attending'),
        ('not_attending', 'Not Attending'),
        ('maybe', 'Maybe'),
    ]
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='rsvps')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='event_rsvps')
    status = models.CharField(max_length=20, choices=RSVP_STATUS, default='attending')
    attended = models.BooleanField(default=False, help_text="Mark if student actually attended")
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['event', 'student']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student} - {self.event.title} ({self.get_status_display()})"

class LoginActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_activities', null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='Success')

    class Meta:
        verbose_name_plural = "Login Activities"
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user} - {self.timestamp}"

class AuditLog(models.Model):
    ACTION_CHOICES = (
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    model_name = models.CharField(max_length=50)
    object_id = models.CharField(max_length=50, null=True, blank=True)
    object_repr = models.CharField(max_length=200, null=True, blank=True)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    changes = models.TextField(null=True, blank=True) # JSON string or text summary
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.action} {self.model_name} by {self.user}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    link = models.CharField(max_length=255, blank=True, null=True) # Optional link to action

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user}: {self.title}"

class Payment(models.Model):
    PAYMENT_STATUS = (
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
    )
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='payments')
    transaction_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    phone_number = models.CharField(max_length=15)
    reference = models.CharField(max_length=50, default='Accommodation')
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='Pending')
    checkout_request_id = models.CharField(max_length=100, blank=True, null=True) # For tracking STK Push
    description = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student} - {self.amount} - {self.status}"
