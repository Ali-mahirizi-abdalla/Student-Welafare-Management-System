from django.contrib import admin
from .models import LibraryUser, BorrowedBook, LibraryFine, LibraryNews

admin.site.register(LibraryUser)
admin.site.register(BorrowedBook)
admin.site.register(LibraryFine)
admin.site.register(LibraryNews)
