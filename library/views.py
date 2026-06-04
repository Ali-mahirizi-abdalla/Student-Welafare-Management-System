from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from datetime import date, timedelta
from .models import LibrarySettings, LibraryUser, Book, BorrowedBook, LibraryFine, LibraryNews

# Student Views
@login_required
def student_library(request):
    """Student library dashboard"""
    try:
        library_user = LibraryUser.objects.get(user=request.user)
        borrowed_books = BorrowedBook.objects.filter(library_user=library_user, status='BORROWED')
        fines = LibraryFine.objects.filter(library_user=library_user, paid=False)
        news = LibraryNews.objects.filter(is_active=True)[:5]
        settings = LibrarySettings.objects.first()
    except LibraryUser.DoesNotExist:
        library_user = None
        borrowed_books = []
        fines = []
        news = []
        settings = None
    
    context = {
        'library_user': library_user,
        'borrowed_books': borrowed_books,
        'total_fines': sum(f.amount for f in fines),
        'news': news,
        'settings': settings,
    }
    return render(request, 'library/student_library.html', context)

@login_required
def borrowed_books(request):
    """List student's borrowed books"""
    library_user = LibraryUser.objects.get(user=request.user)
    books = BorrowedBook.objects.filter(library_user=library_user)
    return render(request, 'library/borrowed_books.html', {'books': books})

@login_required
def pay_fine(request, fine_id):
    """Pay library fine"""
    fine = get_object_or_404(LibraryFine, id=fine_id, library_user__user=request.user)
    # Integration with existing payments system
    return redirect('library:student_library')

# Librarian Views (Staff Only)
@staff_member_required
def librarian_dashboard(request):
    """Librarian main dashboard"""
    try:
        total_books = Book.objects.count()
        borrowed_books = BorrowedBook.objects.filter(status='BORROWED').count()
        overdue_books = BorrowedBook.objects.filter(status='OVERDUE').count()
        pending_fines = LibraryFine.objects.filter(paid=False).count()
        total_fines_amount = sum(f.amount for f in LibraryFine.objects.filter(paid=False))
        registered_users = LibraryUser.objects.count()
        suspended_users = LibraryUser.objects.filter(is_suspended=True).count()
        
        context = {
            'total_books': total_books,
            'borrowed_books': borrowed_books,
            'overdue_books': overdue_books,
            'pending_fines': pending_fines,
            'total_fines_amount': total_fines_amount,
            'registered_users': registered_users,
            'suspended_users': suspended_users,
        }
        return render(request, 'library/librarian_dashboard.html', context)
    except Exception as e:
        import traceback
        import logging
        logger = logging.getLogger(__name__)
        logger.error("Library dashboard 500 error:\n" + traceback.format_exc())
        from django.http import HttpResponseServerError
        return HttpResponseServerError(f"<pre style='padding:20px'><b>Library Error (shown for debugging):</b>\n\n{traceback.format_exc()}</pre>")

@staff_member_required
def book_list(request):
    """List all books"""
    books = Book.objects.all()
    return render(request, 'library/book_list.html', {'books': books})

@staff_member_required
def add_book(request):
    """Add new book"""
    if request.method == 'POST':
        book = Book.objects.create(
            title=request.POST.get('title'),
            author=request.POST.get('author'),
            isbn=request.POST.get('isbn'),
            category=request.POST.get('category'),
            publisher=request.POST.get('publisher'),
            year=request.POST.get('year'),
            total_copies=request.POST.get('total_copies', 1),
            location=request.POST.get('location'),
        )
        messages.success(request, f'Book "{book.title}" added successfully')
        return redirect('library:book_list')
    return render(request, 'library/add_book.html')

@staff_member_required
def edit_book(request, book_id):
    """Edit book details"""
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        book.title = request.POST.get('title')
        book.author = request.POST.get('author')
        book.isbn = request.POST.get('isbn')
        book.category = request.POST.get('category')
        book.publisher = request.POST.get('publisher')
        book.year = request.POST.get('year')
        book.total_copies = request.POST.get('total_copies')
        book.location = request.POST.get('location')
        book.save()
        messages.success(request, f'Book "{book.title}" updated successfully')
        return redirect('library:book_list')
    return render(request, 'library/edit_book.html', {'book': book})

@staff_member_required
def issue_book(request):
    """Issue a book to a student"""
    if request.method == 'POST':
        library_card = request.POST.get('library_card')
        book_id = request.POST.get('book_id')
        
        try:
            library_user = LibraryUser.objects.get(library_card_number=library_card, is_active=True)
            book = Book.objects.get(id=book_id, available_copies__gt=0)
            
            settings = LibrarySettings.objects.first()
            due_date = date.today() + timedelta(days=settings.max_borrow_days if settings else 14)
            
            BorrowedBook.objects.create(
                library_user=library_user,
                book=book,
                due_date=due_date
            )
            
            book.available_copies -= 1
            book.save()
            
            messages.success(request, f'Book "{book.title}" issued to {library_user.user.username}')
        except LibraryUser.DoesNotExist:
            messages.error(request, 'Invalid or inactive library card')
        except Book.DoesNotExist:
            messages.error(request, 'Book not available')
    
    books = Book.objects.filter(available_copies__gt=0)
    return render(request, 'library/issue_book.html', {'books': books})

@staff_member_required
def return_book(request):
    """Return a borrowed book"""
    if request.method == 'POST':
        book_id = request.POST.get('book_id')
        borrowed = BorrowedBook.objects.filter(book_id=book_id, status='BORROWED').first()
        
        if borrowed:
            borrowed.status = 'RETURNED'
            borrowed.returned_date = date.today()
            borrowed.save()
            
            borrowed.book.available_copies += 1
            borrowed.book.save()
            
            # Calculate fine if overdue
            if borrowed.days_overdue > 0:
                settings = LibrarySettings.objects.first()
                fine_amount = borrowed.days_overdue * (settings.fine_per_day if settings else 20)
                LibraryFine.objects.create(
                    library_user=borrowed.library_user,
                    borrowed_book=borrowed,
                    amount=fine_amount,
                    reason=f'Overdue by {borrowed.days_overdue} days'
                )
                messages.warning(request, f'Book returned. Fine: KES {fine_amount}')
            else:
                messages.success(request, 'Book returned successfully')
        else:
            messages.error(request, 'Book not found or already returned')
    
    borrowed_books = BorrowedBook.objects.filter(status='BORROWED')
    return render(request, 'library/return_book.html', {'borrowed_books': borrowed_books})

@staff_member_required
def library_users(request):
    """List all library users"""
    users = LibraryUser.objects.all()
    return render(request, 'library/library_users.html', {'users': users})

@staff_member_required
def fine_list(request):
    """List all fines"""
    fines = LibraryFine.objects.filter(paid=False)
    return render(request, 'library/fine_list.html', {'fines': fines})

@staff_member_required
def restricted_users(request):
    """List suspended, expelled, blocked users"""
    suspended = LibraryUser.objects.filter(is_suspended=True)
    expelled = LibraryUser.objects.filter(is_expelled=True)
    blocked = LibraryUser.objects.filter(is_blocked=True)
    
    context = {
        'suspended': suspended,
        'expelled': expelled,
        'blocked': blocked,
    }
    return render(request, 'library/restricted_users.html', context)

@staff_member_required
def library_reports(request):
    """Generate library reports"""
    # Report generation logic
    return render(request, 'library/reports.html')

def myloft_redirect(request):
    """Redirect to MyLOFT portal"""
    return redirect('https://myloft.campus-care.co.ke')
