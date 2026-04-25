from django.contrib import admin
from .models import Booking, BookingRoom


class BookingRoomInline(admin.TabularInline):
    model = BookingRoom
    extra = 0
    readonly_fields = ['price_snapshot']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['booking_ref', 'user', 'check_in', 'check_out',
                    'guest_count', 'total_price', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['booking_ref', 'user__email']
    readonly_fields = ['booking_ref', 'created_at']
    inlines = [BookingRoomInline]