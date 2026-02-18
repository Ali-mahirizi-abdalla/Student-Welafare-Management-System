from django.contrib import admin
from .models import Subscription

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('plan', 'status', 'start_date', 'end_date', 'amount_paid', 'created_at')
    list_filter = ('status', 'plan', 'created_at')
    search_fields = ('transaction_id', 'status')
    readonly_fields = ('created_at', 'updated_at')
