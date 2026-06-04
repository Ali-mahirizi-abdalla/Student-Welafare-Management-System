from django.db import models
from django.conf import settings
from datetime import date, timedelta

class LibrarySettings(models.Model):
    """Global library settings - separate from other system settings"""
    fine_per_day = models.DecimalField(max_digits=10, decimal_places=2, default=20.00)
    max_borrow_days = models.IntegerField(default=14)
    max_books_per_student = models.IntegerField(default=5)
    max_renewals = models.IntegerField(default=2)
    library_open_time = models.CharField(max_length=20, default="8:00 AM")
    library_close_time = models.CharField(max_length=20, default="8:00 PM")
    
    def __str__(self):
        return "Library Settings"

class LibraryUser(models.Model):
    """Library account for each student - separate from student model"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='library_account')
    library_card_number = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    is_suspended = models.BooleanField(default=False)
    is_expelled = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    studentship_expiry = models.DateField()
    suspension_reason = models.TextField(blank=True)
    suspension_end_date = models.DateField(null=True, blank=True)
    blocked_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.library_card_number}"
    
    @property
    def has_active_account(self):
        return self.is_active and not self.is_suspended and not self.is_expelled and not self.is_blocked

class Book(models.Model):
    """Book inventory"""
    CATEGORY_CHOICES = [
        ('FICTION', 'Fiction'),
        ('NON_FICTION', 'Non-Fiction'),
        ('TECHNICAL', 'Technical'),
        ('ACADEMIC', 'Academic'),
        ('REFERENCE', 'Reference'),
        ('JOURNAL', 'Journal'),
    ]
    title = models.CharField(max_length=300)
    author = models.CharField(max_length=200)
    isbn = models.CharField(max_length=20, unique=True, blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='ACADEMIC')
    publisher = models.CharField(max_length=200, blank=True)
    year = models.IntegerField(null=True, blank=True)
    total_copies = models.IntegerField(default=1)
    available_copies = models.IntegerField(default=1)
    location = models.CharField(max_length=100, blank=True, help_text="Shelf/Rack location")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    @property
    def is_available(self):
        return self.available_copies > 0

class BorrowedBook(models.Model):
    STATUS_CHOICES = [
        ('BORROWED', 'Borrowed'),
        ('RETURNED', 'Returned'),
        ('OVERDUE', 'Overdue'),
        ('LOST', 'Lost'),
    ]
    library_user = models.ForeignKey(LibraryUser, on_delete=models.CASCADE, related_name='borrowed_books')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='borrowings')
    borrowed_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    returned_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='BORROWED')
    renewed_count = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.book.title} - {self.library_user.user.username}"
    
    @property
    def days_overdue(self):
        if self.status == 'OVERDUE' and not self.returned_date:
            return max(0, (date.today() - self.due_date).days)
        return 0
    
    @property
    def fine_amount(self):
        if self.status == 'OVERDUE':
            settings = LibrarySettings.objects.first()
            fine_per_day = settings.fine_per_day if settings else 20
            return self.days_overdue * fine_per_day
        return 0

class LibraryFine(models.Model):
    library_user = models.ForeignKey(LibraryUser, on_delete=models.CASCADE, related_name='fines')
    borrowed_book = models.ForeignKey(BorrowedBook, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.CharField(max_length=200)
    paid = models.BooleanField(default=False)
    paid_date = models.DateField(null=True, blank=True)
    created_date = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.library_user.user.username} - KES {self.amount}"

class LibraryNews(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title
