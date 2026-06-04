from django.contrib import admin
from .models import LibrarySettings, LibraryUser, Book, BorrowedBook, LibraryFine, LibraryNews

@admin.register(LibrarySettings)
class LibrarySettingsAdmin(admin.ModelAdmin):
    list_display = ['fine_per_day', 'max_borrow_days', 'max_books_per_student']

@admin.register(LibraryUser)
class LibraryUserAdmin(admin.ModelAdmin):
    list_display = ['user', 'library_card_number', 'is_active', 'is_suspended', 'is_expelled', 'is_blocked']
    list_filter = ['is_active', 'is_suspended', 'is_expelled', 'is_blocked']
    search_fields = ['user__username', 'user__email', 'library_card_number']

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'isbn', 'category', 'total_copies', 'available_copies']
    list_filter = ['category']
    search_fields = ['title', 'author', 'isbn']

@admin.register(BorrowedBook)
class BorrowedBookAdmin(admin.ModelAdmin):
    list_display = ['book', 'library_user', 'borrowed_date', 'due_date', 'status']
    list_filter = ['status']
    search_fields = ['book__title', 'library_user__user__username']

@admin.register(LibraryFine)
class LibraryFineAdmin(admin.ModelAdmin):
    list_display = ['library_user', 'amount', 'paid', 'created_date']
    list_filter = ['paid']

@admin.register(LibraryNews)
class LibraryNewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_at', 'is_active']
