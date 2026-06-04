from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import LibraryUser, BorrowedBook, LibraryFine, LibraryNews
from .myloft_integration import MyLOFTIntegration
from django.utils import timezone
import datetime

@login_required
def student_library(request):
    """Student Dashboard for Library Management"""
    # Assuming user is a student, we try to get or create their LibraryUser profile
    try:
        student = request.user.student_profile
    except AttributeError:
        messages.error(request, "Only students can access this page.")
        return redirect('hms:dashboard')

    # Dummy logic to create LibraryUser if not exists (for demo)
    library_user, created = LibraryUser.objects.get_or_create(
        student=student,
        defaults={
            'library_card_number': f"LIB-{student.university_id or student.id}",
            'studentship_expiry': timezone.now().date() + datetime.timedelta(days=365*2)
        }
    )

    borrowed_books = BorrowedBook.objects.filter(library_user=library_user, status='BORROWED')
    fines = LibraryFine.objects.filter(library_user=library_user, paid=False)
    total_fines = sum(fine.amount for fine in fines)
    news = LibraryNews.objects.filter(is_active=True).order_by('-created_at')[:3]

    # Check for overdue books
    today = timezone.now().date()
    overdue_books = []
    for book in borrowed_books:
        if book.due_date < today:
            overdue_books.append(book)
            # You might want to update status to OVERDUE here or generate fines

    context = {
        'library_user': library_user,
        'borrowed_books': borrowed_books,
        'overdue_books': overdue_books,
        'total_fines': total_fines,
        'news': news,
    }
    return render(request, 'library/student_library.html', context)

@login_required
def renew_book(request, book_id):
    """Dummy view for renewing a book"""
    if request.method == 'POST':
        messages.success(request, 'Book renewed successfully!')
    return redirect('library:student_library')

@login_required
def pay_fine(request):
    """Dummy view for paying fines, redirects to payment module"""
    messages.info(request, 'Redirecting to payment gateway...')
    # In a real scenario, this would redirect to hms:payments or similar
    return redirect('library:student_library')

@login_required
def librarian_dashboard(request):
    """Librarian Dashboard"""
    # Check if user is librarian
    if not hasattr(request.user, 'staff_profile') or request.user.staff_profile.role != 'librarian':
        messages.error(request, "Access Denied. Librarian role required.")
        return redirect('hms:dashboard')
    
    # Context data for the librarian dashboard
    suspended_users = LibraryUser.objects.filter(is_suspended=True)
    expelled_users = LibraryUser.objects.filter(is_expelled=True)
    
    context = {
        'suspended_users': suspended_users,
        'expelled_users': expelled_users,
        # Add blocked users, reports, etc. as needed
    }
    return render(request, 'library/librarian_dashboard.html', context)

@login_required
def issue_book(request):
    """Dummy view to issue book"""
    if request.method == 'POST':
        messages.success(request, 'Book issued successfully!')
    return redirect('library:librarian_dashboard')

@login_required
def return_book(request):
    """Dummy view to return book"""
    if request.method == 'POST':
        messages.success(request, 'Book returned successfully!')
    return redirect('library:librarian_dashboard')

@login_required
def block_student(request):
    """Dummy view to block student"""
    if request.method == 'POST':
        messages.success(request, 'Student blocked successfully!')
    return redirect('library:librarian_dashboard')

@login_required
def myloft_redirect(request):
    """Redirect to MyLOFT application"""
    # They provided the URL in the mockup
    myloft_url = "https://myloft.campus-care.co.ke"
    return redirect(myloft_url)
