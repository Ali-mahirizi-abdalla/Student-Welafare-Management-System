from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, datetime
import json

class AuditLog(models.Model):
    """
    Audit Log to track all critical system activities.
    """
    ACTION_CHOICES = [
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('APPROVE', 'Approve'),
        ('REJECT', 'Reject'),
        ('EXPORT', 'Export'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=50, blank=True, null=True)
    object_id = models.CharField(max_length=50, blank=True, null=True)
    object_repr = models.CharField(max_length=200, blank=True, null=True)
    details = models.TextField(blank=True, null=True, help_text="JSON representation of changes")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        permissions = [
            ("view_audit_log", "Can view audit logs"),
            ("export_audit_log", "Can export audit logs"),
        ]

    def __str__(self):
        return f"{self.user} - {self.action} - {self.timestamp}"

class Student(models.Model):
    """Extended profile for students"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    university_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    profile_image = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    timetable = models.FileField(upload_to='timetables/', blank=True, null=True)
    room_number = models.CharField(max_length=10, blank=True, null=True)
    
    RESIDENCE_TYPE_CHOICES = [
        ('hostel', 'In Hostel'),
        ('off_campus', 'Off-Campus (Rental)'),
    ]
    residence_type = models.CharField(max_length=20, choices=RESIDENCE_TYPE_CHOICES, default='hostel')

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('others', 'Others'),
    ]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)

    DISABILITY_CHOICES = [
        ('none', 'None'),
        ('physical', 'Physical Disability'),
        ('visual', 'Visual Impairment'),
        ('hearing', 'Hearing Impairment'),
        ('mental', 'Mental Health Condition'),
        ('others', 'Others'),
    ]
    disability = models.CharField(max_length=20, choices=DISABILITY_CHOICES, default='none')
    disability_details = models.TextField(blank=True, null=True, help_text="Specify details if 'Others' is selected")

    program_of_study = models.CharField(max_length=100, blank=True, null=True, help_text="Department or Program of Study")
    
    HOSTEL_CHOICES = [
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ('6', '6'),
        ('7', '7'),
        ('8', '8'),
        ('9', '9'),
        ('10', '10'),
    ]
    hostel = models.CharField(max_length=20, choices=HOSTEL_CHOICES, blank=True, null=True)
    
    COUNTY_CHOICES = [
        ('baringo', 'Baringo'),
        ('bomet', 'Bomet'),
        ('bungoma', 'Bungoma'),
        ('busia', 'Busia'),
        ('elgeyo_marakwet', 'Elgeyo Marakwet'),
        ('embu', 'Embu'),
        ('garissa', 'Garissa'),
        ('homa_bay', 'Homa Bay'),
        ('isiolo', 'Isiolo'),
        ('kajiado', 'Kajiado'),
        ('kakamega', 'Kakamega'),
        ('kericho', 'Kericho'),
        ('kiambu', 'Kiambu'),
        ('kilifi', 'Kilifi'),
        ('kirinyaga', 'Kirinyaga'),
        ('kisii', 'Kisii'),
        ('kisumu', 'Kisumu'),
        ('kitui', 'Kitui'),
        ('kwale', 'Kwale'),
        ('laikipia', 'Laikipia'),
        ('lamu', 'Lamu'),
        ('machakos', 'Machakos'),
        ('makueni', 'Makueni'),
        ('mandera', 'Mandera'),
        ('marsabit', 'Marsabit'),
        ('meru', 'Meru'),
        ('migori', 'Migori'),
        ('mombasa', 'Mombasa'),
        ('muranga', "Murang'a"),
        ('nairobi', 'Nairobi'),
        ('nakuru', 'Nakuru'),
        ('nandi', 'Nandi'),
        ('narok', 'Narok'),
        ('nyamira', 'Nyamira'),
        ('nyandarua', 'Nyandarua'),
        ('nyeri', 'Nyeri'),
        ('samburu', 'Samburu'),
        ('siaya', 'Siaya'),
        ('taita_taveta', 'Taita Taveta'),
        ('tana_river', 'Tana River'),
        ('tharaka_nithi', 'Tharaka Nithi'),
        ('trans_nzoia', 'Trans Nzoia'),
        ('turkana', 'Turkana'),
        ('uasin_gishu', 'Uasin Gishu'),
        ('vihiga', 'Vihiga'),
        ('wajir', 'Wajir'),
        ('west_pokot', 'West Pokot'),
    ]
    county = models.CharField(max_length=50, choices=COUNTY_CHOICES, blank=True, null=True)
    
    is_warden = models.BooleanField(default=False)
    is_on_attachment = models.BooleanField(default=False, help_text="Is the student currently on industrial attachment?")
    is_graduating = models.BooleanField(default=False, help_text="Is the student in their graduating semester/year?")
    
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
    location = models.CharField(max_length=100, help_text="Specific location, e.g., Room 101, Common Room", blank=True, null=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    image = models.ImageField(upload_to='maintenance_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    admin_notes = models.TextField(blank=True, help_text="Notes from admin/warden", default='')

    class Meta:
        ordering = ['-created_at']


class StaffProfile(models.Model):
    ROLE_CHOICES = [
        # Executive
        ('VC', 'Vice Chancellor'),
        ('DVC_AFP', 'DVC, Administration, Finance and Planning'),
        ('DVC_ASA', 'DVC, Academic and Student Affairs'),
        ('DVC_RE', 'DVC, Research and Extension'),
        
        # Directors (Academic Admin)
        ('DIR_QA', 'Director, Quality Assurance'),
        ('DIR_RM', 'Director, Resource Mobilisation'),
        ('DIR_RPDO', 'Director, Research, Production, Development, and Outreach'),
        ('DIR_IEC', 'Director, Innovation, Entrepreneurship and Commercialization'),
        ('DIR_TVET', 'Director, TVET'),
        ('DIR_BGS', 'Director, Board of Graduate Studies'),
        ('DIR_BUS', 'Director, Board of Undergraduate Studies'),
        
        # Registrars
        ('REG_AP', 'Registrar, Administration and Planning'),
        ('REG_ASA', 'Registrar, Academic and Student Affairs'),
        ('DEP_REG_EXAM', 'Deputy Registrar, Examinations'),
        ('DEP_REG_AP', 'Deputy Registrar, Academic Programmes'),
        ('DEP_REG_ADM', 'Deputy Registrar, Admissions'),
        
        # School of Agricultural Sciences & Agribusiness
        ('DEAN_AGRI', 'Dean, School of Agricultural Sciences & Agribusiness'),
        ('DEPT_ANIMAL', 'Department of Animal Sciences'),
        ('DEPT_CROP', 'Department of Crop Sciences'),
        
        # School of Business and Economics
        ('DEAN_BE', 'Dean, School of Business and Economics'),
        ('DEPT_BME', 'Department of Business Management & Economics'),
        ('DEPT_HTM', 'Department of Hospitality and Tourism Management'),
        
        # School of Education
        ('DEAN_EDU', 'Dean, School of Education'),
        ('COD_CIT', 'COD, Department of Curriculum Instruction and Technology'),
        ('COD_EP_SN', 'COD, Department of Educational Psychology and Special Needs'),
        ('COD_EF', 'COD, Department of Educational Foundations'),
        ('COD_EAEP', 'COD, Department of Educational Administration, Economics and Planning'),
        
        # School of Environmental and Earth Sciences
        ('DEAN_EES', 'Dean, School of Environmental and Earth Sciences'),
        ('DEPT_ES', 'Department of Environmental Sciences'),
        ('DEPT_CD', 'Department of Community Development'),
        
        # School of Health and Human Sciences
        ('DEAN_HHS', 'Dean, School of Health and Human Sciences'),
        ('DEPT_AP', 'Department of Anatomy and Physiology'),
        ('DEPT_PH', 'Department of Public Health'),
        ('DEPT_FND', 'Department of Food Nutrition and Dietetics'),
        ('DEPT_NURSING', 'Department of Nursing'),
        
        # School of Humanities and Social Sciences
        ('DEAN_HSS', 'Dean, School of Humanities & Social Sciences'),
        ('DEPT_SS', 'Department of Social Sciences'),
        ('DEPT_LLL', 'Department of Languages, Linguistics & Literature'),
        ('DEPT_PRS', 'Department of Philosophy and Religious Studies'),
        
        # School of Pure and Applied Sciences
        ('DEAN_PAS', 'Dean, School of Pure & Applied Sciences'),
        ('DEPT_BS', 'Department of Biological Sciences'),
        ('DEPT_CHEM', 'Department of Chemistry'),
        ('DEPT_BB', 'Department of Biochemistry and Biotechnology'),
        ('DEPT_PHYSICS', 'Department of Physics'),
        ('DEPT_MCS', 'Department of Mathematics and Computer Science'),
        
        # Support/Misc
        ('LAB_IN_CHARGE', 'In charge Laboratories'),
        ('PUBREC_MGR', 'Manager, PUBReC'),
        ('COORDINATOR_MTLC', 'Coordinator, Mombasa Teaching and Learning Centre'),
        ('DEAN_STUDENTS', 'Dean of Students'),
        ('SPORTS_OFFICER', 'Sports Officer'),
        ('ACU_COORD', 'Coordinator, Aids Control Unit'),
        ('CATERING_IN_CHARGE', 'In charge, Students Catering Unit'),
        ('HEALTH_UNIT_HEAD', 'Head of Health Unit'),
        ('COUNSELLING_IN_CHARGE', 'In charge, Counselling'),
        ('ACC_IN_CHARGE', 'In charge, Accommodation (M&F)'),
        
        # Section Heads
        ('ERC', 'Ethics Review Committee'),
        ('FINANCE_OFFICER', 'Finance Officer'),
        ('HR_MANAGER', 'Human Resource Manager'),
        ('INTERNAL_AUDITOR', 'Internal Auditor'),
        ('LEGAL_HEAD', 'Head, Corporate and Legal and Council Affairs'),
        ('FARM_MANAGER', 'Farm Manager'),
        ('RESOURCE_CENTER_IN_CHARGE', 'In charge, Resource Centre'),
        ('LIBRARY_HEAD', 'Head of University Library'),
        ('ICT_MANAGER', 'Manager, ICT'),
        ('SECURITY_CHIEF', 'Chief Security Officer'),
        ('PROCUREMENT_HEAD', 'Head, Procurement and Supplies'),
        ('ESTATES_HEAD', 'Head, Estates and Infrastructure Planning'),
        ('MAINTENANCE_HEAD', 'Head, Maintenance'),
        ('TRANSPORT_HEAD', 'Head, Transport'),
        ('REGISTRY_CLERK', 'Registry Clerk'),
        ('KUDHEIHA', 'KUDHEIHA'),
        ('KUSU', 'KUSU'),
        ('UASU', 'UASU'),
        
        # Legacy mappings (for backward compatibility)
        ('DEFERMENT', 'Deferment Manager (Legacy)'),
        ('MAINTENANCE_HOSTEL', 'Maintenance & Hostel Manager (Legacy)'),
        ('ACTIVITIES_ROOMS', 'Activities & Rooms Manager (Legacy)'),
        ('NEWS_ALERT', 'News & Announcements Manager (Legacy)'),
        ('VISITORS', 'Visitor Log Manager (Legacy)'),
        ('AUDIT_LOGS', 'Audit Compliance Officer (Legacy)'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    national_id = models.CharField(max_length=20, unique=True, verbose_name="Role ID / National ID")
    phone = models.CharField(max_length=15)

    def get_category(self):
        """Categorize roles for permission logic"""
        role = self.role
        if role in ['VC', 'DVC_AFP', 'DVC_ASA', 'DVC_RE', 'REG_AP', 'REG_ASA']:
            return 'EXECUTIVE'
        if role.startswith('DEAN_') or role.startswith('DIR_') or role.startswith('DEP_REG_'):
            return 'ACADEMIC_ADMIN'
        if role.startswith('COD_') or role.startswith('DEPT_'):
            return 'SCHOOL_DEPT'
        if role in ['FINANCE_OFFICER', 'HR_MANAGER', 'INTERNAL_AUDITOR', 'LEGAL_HEAD', 'PROCUREMENT_HEAD', 'AUDIT_LOGS']:
            return 'FINANCE_ADMIN'
        if role in ['DEAN_STUDENTS', 'SPORTS_OFFICER', 'ACU_COORD', 'CATERING_IN_CHARGE', 'HEALTH_UNIT_HEAD', 'COUNSELLING_IN_CHARGE', 'ACC_IN_CHARGE', 'ACTIVITIES_ROOMS', 'NEWS_ALERT']:
            return 'STUDENT_SERVICES'
        if role in ['ICT_MANAGER', 'SECURITY_CHIEF', 'ESTATES_HEAD', 'MAINTENANCE_HEAD', 'TRANSPORT_HEAD', 'LAB_IN_CHARGE', 'MAINTENANCE_HOSTEL', 'VISITORS']:
            return 'TECHNICAL_ESTATES'
        return 'GENERAL_STAFF'

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_role_display()}"

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
    CATEGORY_CHOICES = [
        ('male_student', 'Male Student'),
        ('female_student', 'Female Student'),
        ('lgbtq', 'LGBTQ'),
        ('male_parent', 'Male Parents'),
        ('female_parent', 'Female Parents'),
        ('pwd', 'PWD'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='visitors')
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='male_student')
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

class Message(models.Model):
    """Chat messages between users"""
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    attachment = models.FileField(upload_to='chat_attachments/', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"From {self.sender} to {self.recipient}: {self.content[:20]}"

class Room(models.Model):
    """Rooms in hostels"""
    ROOM_TYPES = [
        ('single', 'Single'), ('double', 'Double'), ('triple', 'Triple'), ('quad', 'Quad')
    ]
    room_number = models.CharField(max_length=10, unique=True)
    floor = models.IntegerField()
    block = models.CharField(max_length=50, blank=True)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES, default='double')
    capacity = models.IntegerField(default=2)
    is_available = models.BooleanField(default=True)
    amenities = models.TextField(blank=True, help_text="List amenities (e.g., AC, attached bathroom)")
    price_per_semester = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['block', 'floor', 'room_number']

    def __str__(self):
        return f"{self.room_number} ({self.block})"

class RoomAssignment(models.Model):
    """Assigning students to rooms"""
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='assignments')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='room_assignments')
    bed_number = models.IntegerField(null=True, blank=True)
    assigned_date = models.DateField(default=timezone.now)
    checkout_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-assigned_date']

    def __str__(self):
        return f"{self.student} in {self.room}"

class RoomChangeRequest(models.Model):
    """Requests to change rooms"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='room_change_requests')
    current_room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, related_name='change_requests_from')
    requested_room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True, related_name='change_requests_to')
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')
    ], default='pending')
    admin_notes = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_room_changes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Change Request: {self.student}"

class LoginActivity(models.Model):
    """Track user login activities"""
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

class Notification(models.Model):
    """System notifications for users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    link = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.title}"

class Payment(models.Model):
    """M-Pesa payment records"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='payments')
    transaction_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    phone_number = models.CharField(max_length=15)
    reference = models.CharField(max_length=50, default='Accommodation')
    status = models.CharField(max_length=20, choices=[
        ('Pending', 'Pending'), ('Completed', 'Completed'), ('Failed', 'Failed')
    ], default='Pending')
    checkout_request_id = models.CharField(max_length=100, null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment {self.transaction_id or 'Pending'} - {self.student}"


class LostItem(models.Model):
    """Model for Lost and Found items"""
    STATUS_CHOICES = [
        ('LOST', 'Lost'),
        ('FOUND', 'Found'),
        ('CLAIMED', 'Claimed'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    location = models.CharField(max_length=100, help_text="Where it was lost or found")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='LOST')
    contact_phone = models.CharField(max_length=15, help_text="Contact number for the finder/owner")
    image = models.ImageField(upload_to='lost_found/', blank=True, null=True)
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reported_items')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.get_status_display()}: {self.name}"
