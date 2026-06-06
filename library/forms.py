from django import forms
from .models import Book, LibrarySettings, BorrowedBook, LibraryFine

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'isbn', 'category', 'publisher', 'year', 'total_copies', 'location']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter book title'}),
            'author': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter author name'}),
            'isbn': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter ISBN'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'publisher': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter publisher'}),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Publication year'}),
            'total_copies': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Shelf/Rack location'}),
        }

class LibrarySettingsForm(forms.ModelForm):
    class Meta:
        model = LibrarySettings
        fields = '__all__'
        widgets = {
            'fine_per_day': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'max_borrow_days': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_books_per_student': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_renewals': forms.NumberInput(attrs={'class': 'form-control'}),
            'library_open_time': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '8:00 AM'}),
            'library_close_time': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '8:00 PM'}),
        }

class IssueBookForm(forms.ModelForm):
    class Meta:
        model = BorrowedBook
        fields = ['library_user', 'book', 'due_date']
        widgets = {
            'library_user': forms.Select(attrs={'class': 'form-select'}),
            'book': forms.Select(attrs={'class': 'form-select'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
