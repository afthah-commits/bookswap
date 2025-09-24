from django.contrib import admin
from .models import Book, SwapRequest, Transaction, Review

admin.site.register(Book)
admin.site.register(SwapRequest)
admin.site.register(Transaction)
admin.site.register(Review)

