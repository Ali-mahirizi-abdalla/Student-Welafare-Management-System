from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from datetime import date, timedelta
from .models import LibrarySettings, LibraryUser, Book, BorrowedBook, LibraryFine, LibraryNews
from .forms import BookForm, IssueBookForm

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
    return render(request, 'library/borrowed_list.html', {'books': books})

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
    total_books = Book.objects.count()
    borrowed_count = BorrowedBook.objects.filter(status='BORROWED').count()
    overdue_books = BorrowedBook.objects.filter(status='OVERDUE').count()
    pending_fines = LibraryFine.objects.filter(paid=False).count()
    total_fines_amount = sum(f.amount for f in LibraryFine.objects.filter(paid=False))
    registered_users = LibraryUser.objects.count()
    suspended_users = LibraryUser.objects.filter(is_suspended=True).count()
    
    context = {
        'total_books': total_books,
        'borrowed_books': borrowed_count,
        'overdue_books': overdue_books,
        'pending_fines': pending_fines,
        'total_fines_amount': total_fines_amount,
        'registered_users': registered_users,
        'suspended_users': suspended_users,
    }
    return render(request, 'library/librarian_dashboard.html', context)

@staff_member_required
def book_list(request):
    """List all books"""
    books = Book.objects.all()
    return render(request, 'library/book_list.html', {'books': books})

@staff_member_required
def add_book(request):
    """Add new book"""
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Book "{form.instance.title}" added successfully')
            return redirect('library:book_list')
    else:
        form = BookForm()
    return render(request, 'library/book_form.html', {'form': form, 'title': 'Add New Book'})

@staff_member_required
def edit_book(request, book_id):
    """Edit book details"""
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, f'Book "{book.title}" updated successfully')
            return redirect('library:book_list')
    else:
        form = BookForm(instance=book)
    return render(request, 'library/book_form.html', {'form': form, 'book': book, 'title': f'Edit: {book.title}'})

@staff_member_required
def delete_book(request, book_id):
    """Delete a book"""
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        title = book.title
        book.delete()
        messages.success(request, f'Book "{title}" deleted successfully')
        return redirect('library:book_list')
    return render(request, 'library/confirm_delete.html', {
        'object': book,
        'title': f'Delete Book: {book.title}',
        'back_url': 'library:book_list',
    })

@staff_member_required
def category_list(request):
    """List book categories"""
    # Categories are defined as choices on the Book model
    categories = Book.CATEGORY_CHOICES
    books_by_category = []
    for code, name in categories:
        count = Book.objects.filter(category=code).count()
        books_by_category.append({'name': name, 'code': code, 'count': count})
    return render(request, 'library/category_list.html', {'categories': books_by_category})

@staff_member_required
def issue_book(request):
    """Issue a book to a student"""
    if request.method == 'POST':
        form = IssueBookForm(request.POST)
        if form.is_valid():
            borrowed = form.save(commit=False)
            if not borrowed.due_date:
                settings = LibrarySettings.objects.first()
                borrowed.due_date = date.today() + timedelta(days=settings.max_borrow_days if settings else 14)
            borrowed.save()
            
            borrowed.book.available_copies -= 1
            borrowed.book.save()
            
            messages.success(request, f'Book "{borrowed.book.title}" issued to {borrowed.library_user.user.username}')
            return redirect('library:librarian_borrowed_books')
    else:
        form = IssueBookForm()
    return render(request, 'library/issue_book.html', {'form': form})

@staff_member_required
def return_book(request, borrow_id=None):
    """Return a borrowed book"""
    if borrow_id:
        borrowed = get_object_or_404(BorrowedBook, id=borrow_id, status='BORROWED')
        if request.method == 'POST':
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
            return redirect('library:librarian_borrowed_books')
    
    # Handle POST without borrow_id (legacy form)
    if request.method == 'POST' and not borrow_id:
        book_id = request.POST.get('book_id')
        borrowed = BorrowedBook.objects.filter(book_id=book_id, status='BORROWED').first()
        
        if borrowed:
            borrowed.status = 'RETURNED'
            borrowed.returned_date = date.today()
            borrowed.save()
            
            borrowed.book.available_copies += 1
            borrowed.book.save()
            
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
def librarian_borrowed_books(request):
    """List all borrowed books for librarian"""
    borrowed_books = BorrowedBook.objects.all().order_by('-borrowed_date')
    return render(request, 'library/borrowed_list.html', {'borrowed_books': borrowed_books})

@staff_member_required
def renew_book(request, borrow_id):
    """Renew a borrowed book"""
    borrowed = get_object_or_404(BorrowedBook, id=borrow_id, status='BORROWED')
    if request.method == 'POST':
        settings = LibrarySettings.objects.first()
        max_renewals = settings.max_renewals if settings else 2
        
        if borrowed.renewed_count >= max_renewals:
            messages.error(request, f'Maximum renewals ({max_renewals}) reached for this book')
        else:
            borrow_days = settings.max_borrow_days if settings else 14
            borrowed.due_date = date.today() + timedelta(days=borrow_days)
            borrowed.renewed_count += 1
            borrowed.save()
            messages.success(request, f'Book renewed. New due date: {borrowed.due_date}')
    return redirect('library:librarian_borrowed_books')

@staff_member_required
def library_users(request):
    """List all library users"""
    users = LibraryUser.objects.all()
    return render(request, 'library/users_list.html', {'users': users})

@staff_member_required
def user_profile(request, user_id):
    """View a library user's profile"""
    lib_user = get_object_or_404(LibraryUser, id=user_id)
    borrowed_books = BorrowedBook.objects.filter(library_user=lib_user).order_by('-borrowed_date')
    fines = LibraryFine.objects.filter(library_user=lib_user).order_by('-created_date')
    
    context = {
        'lib_user': lib_user,
        'borrowed_books': borrowed_books,
        'fines': fines,
    }
    return render(request, 'library/user_profile.html', context)

@staff_member_required
def restrict_action(request, pk, action):
    """Suspend, block, or reinstate a library user"""
    lib_user = get_object_or_404(LibraryUser, id=pk)
    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        if action == 'suspend':
            lib_user.is_suspended = True
            lib_user.suspension_reason = reason
            lib_user.save()
            messages.warning(request, f'{lib_user.user.username} has been suspended')
        elif action == 'block':
            lib_user.is_blocked = True
            lib_user.blocked_reason = reason
            lib_user.save()
            messages.warning(request, f'{lib_user.user.username} has been blocked')
        elif action == 'reinstate':
            lib_user.is_suspended = False
            lib_user.is_blocked = False
            lib_user.suspension_reason = ''
            lib_user.blocked_reason = ''
            lib_user.suspension_end_date = None
            lib_user.save()
            messages.success(request, f'{lib_user.user.username} has been reinstated')
    return redirect('library:user_profile', user_id=pk)

@staff_member_required
def fine_list(request):
    """List all fines"""
    fines = LibraryFine.objects.filter(paid=False)
    return render(request, 'library/fine_list.html', {'fines': fines})

@staff_member_required
def collect_fine(request, fine_id):
    """Collect/mark a fine as paid"""
    fine = get_object_or_404(LibraryFine, id=fine_id)
    if request.method == 'POST':
        fine.paid = True
        fine.paid_date = date.today()
        fine.save()
        messages.success(request, f'Fine of KES {fine.amount} collected successfully')
        return redirect('library:fine_list')
    return render(request, 'library/collect_fine.html', {'fine': fine})

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

@staff_member_required
def library_settings(request):
    """Library settings management"""
    settings_obj = LibrarySettings.objects.first()
    if not settings_obj:
        settings_obj = LibrarySettings.objects.create()
    
    if request.method == 'POST':
        settings_obj.fine_per_day = request.POST.get('fine_per_day', settings_obj.fine_per_day)
        settings_obj.max_borrow_days = request.POST.get('max_borrow_days', settings_obj.max_borrow_days)
        settings_obj.max_books_per_student = request.POST.get('max_books_per_student', settings_obj.max_books_per_student)
        settings_obj.max_renewals = request.POST.get('max_renewals', settings_obj.max_renewals)
        settings_obj.library_open_time = request.POST.get('library_open_time', settings_obj.library_open_time)
        settings_obj.library_close_time = request.POST.get('library_close_time', settings_obj.library_close_time)
        settings_obj.save()
        messages.success(request, 'Library settings updated successfully')
        return redirect('library:library_settings')
    
    from .forms import LibrarySettingsForm
    form = LibrarySettingsForm(instance=settings_obj)
    return render(request, 'library/settings.html', {'form': form, 'settings': settings_obj})

def myloft_redirect(request):
    """Redirect to MyLOFT portal"""
    return redirect('https://myloft.campus-care.co.ke')
