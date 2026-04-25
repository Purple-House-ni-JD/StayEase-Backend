from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['booking', 'amount', 'method', 'status', 'transaction_ref', 'paid_at']
    list_filter = ['status', 'method']
    search_fields = ['booking__booking_ref', 'transaction_ref']
    readonly_fields = ['booking', 'amount']