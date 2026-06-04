from django import forms
from .models import Book, Category, LibrarySetting, BorrowedBook, LibraryFine

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'isbn', 'category', 'total_copies']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter book title'}),
            'author': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter author name'}),
            'isbn': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter ISBN'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'total_copies': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class LibrarySettingForm(forms.ModelForm):
    class Meta:
        model = LibrarySetting
        fields = '__all__'
        widgets = {
            'daily_fine_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'loan_period_days': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_books_per_student': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_renewals': forms.NumberInput(attrs={'class': 'form-control'}),
            'opening_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'closing_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }

class IssueBookForm(forms.ModelForm):
    class Meta:
        model = BorrowedBook
        fields = ['library_user', 'book', 'due_date']
        widgets = {
            'library_user': forms.Select(attrs={'class': 'form-select select2'}),
            'book': forms.Select(attrs={'class': 'form-select select2'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
