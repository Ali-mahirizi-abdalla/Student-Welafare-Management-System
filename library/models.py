from django.db import models

class LibraryUser(models.Model):
    student = models.OneToOneField('hms.Student', on_delete=models.CASCADE)
    library_card_number = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    is_suspended = models.BooleanField(default=False)
    is_expelled = models.BooleanField(default=False)
    studentship_expiry = models.DateField()
    suspension_reason = models.TextField(blank=True)
    suspension_end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.student} - {self.library_card_number}"

class BorrowedBook(models.Model):
    library_user = models.ForeignKey(LibraryUser, on_delete=models.CASCADE)
    book_title = models.CharField(max_length=300)
    book_author = models.CharField(max_length=200, blank=True)
    isbn = models.CharField(max_length=20, blank=True)
    borrowed_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    returned_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, default='BORROWED')  # BORROWED, RETURNED, OVERDUE

    def __str__(self):
        return f"{self.book_title} by {self.library_user}"

class LibraryFine(models.Model):
    library_user = models.ForeignKey(LibraryUser, on_delete=models.CASCADE)
    borrowed_book = models.ForeignKey(BorrowedBook, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.CharField(max_length=200)
    paid = models.BooleanField(default=False)
    created_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Fine: {self.amount} for {self.library_user}"

class LibraryNews(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title
