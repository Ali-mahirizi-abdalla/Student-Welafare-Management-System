from django.urls import path
from . import views

app_name = 'library'

urlpatterns = [
    # Student views
    path('my-library/', views.student_library, name='student_library'),
    path('borrowed-books/', views.borrowed_books, name='borrowed_books'),
    path('fine-payment/<int:fine_id>/', views.pay_fine, name='pay_fine'),
    
    # Librarian views
    path('librarian/dashboard/', views.librarian_dashboard, name='librarian_dashboard'),
    path('librarian/books/', views.book_list, name='book_list'),
    path('librarian/books/add/', views.add_book, name='add_book'),
    path('librarian/books/edit/<int:book_id>/', views.edit_book, name='edit_book'),
    path('librarian/issue/', views.issue_book, name='issue_book'),
    path('librarian/return/', views.return_book, name='return_book'),
    path('librarian/users/', views.library_users, name='library_users'),
    path('librarian/fines/', views.fine_list, name='fine_list'),
    path('librarian/restricted/', views.restricted_users, name='restricted_users'),
    path('librarian/reports/', views.library_reports, name='library_reports'),
    
    # MyLOFT redirect
    path('myloft/', views.myloft_redirect, name='myloft_redirect'),
]
