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

class MaintenanceRequest(models.Model):
    """Maintenance requests"""
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='maintenance_requests')
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=100, help_text="Specific location, e.g., Room 101, Common Room")
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    image = models.ImageField(upload_to='maintenance_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    admin_notes = models.TextField(blank=True, help_text="Notes from admin/warden")

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.status})"

class Document(models.Model):
    """Uploaded documents for students"""
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='documents/')
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_visible = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class DefermentRequest(models.Model):
    """Student deferment requests (Leave of Absence)"""
    DEFERMENT_TYPES = [
        ('fee_challenges', 'Fee Challenges'),
        ('motherhood_fatherhood', 'Motherhood/Fatherhood'),
        ('special_exams', 'Special Exams'),
        ('sick_role', 'Sick Role (Medical)'),
        ('bereavement', 'Bereavement'),
        ('suspension_expulsion', 'Suspension/Expulsion'),
        ('natural_calamity', 'Natural Calamity'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='deferment_requests')
    start_date = models.DateField()
    end_date = models.DateField()
    deferment_type = models.CharField(max_length=30, choices=DEFERMENT_TYPES, help_text="Select the reason for deferment")
    reason = models.TextField(help_text="Detailed explanation")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_response = models.TextField(blank=True, help_text="Response from admin")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student} - {self.get_deferment_type_display()}"

# Alias for backward compatibility if needed, but DefermentRequest is the primary
LeaveRequest = DefermentRequest

class EmergencyAlert(models.Model):
    """Emergency SOS alerts from students"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='emergency_alerts')
    location = models.CharField(max_length=255, blank=True, help_text="Location when alert was triggered")
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    admin_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"SOS: {self.student} at {self.created_at}"

class Suggestion(models.Model):
    """Anonymous suggestions from students"""
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Suggestion ({self.created_at.strftime('%Y-%m-%d')})"

class Visitor(models.Model):
    """Visitor logbook"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='visitors')
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    id_number = models.CharField(max_length=20, help_text="National ID or Passport Number")
    purpose = models.TextField()
    check_in_time = models.DateTimeField(auto_now_add=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='registered_visitors')

    class Meta:
        ordering = ['-check_in_time']

    def __str__(self):
        return f"{self.name} - Visiting {self.student.user.get_full_name()}"

    def check_out(self):
        """Mark visitor as checked out"""
        self.check_out_time = timezone.now()
        self.is_active = False
        self.save()
