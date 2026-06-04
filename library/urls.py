from django.urls import path
from . import views

app_name = 'library'

urlpatterns = [
    # Student views
    path('my-library/', views.student_library, name='student_library'),
    path('renew/<int:book_id>/', views.renew_book, name='renew_book'),
    path('pay-fine/', views.pay_fine, name='pay_fine'),
    
    # Librarian views (new role)
    path('librarian/', views.librarian_dashboard, name='librarian_dashboard'),
    path('issue-book/', views.issue_book, name='issue_book'),
    path('return-book/', views.return_book, name='return_book'),
    path('block-student/', views.block_student, name='block_student'),
    
    # MyLOFT integration
    path('myloft-redirect/', views.myloft_redirect, name='myloft_redirect'),
]
