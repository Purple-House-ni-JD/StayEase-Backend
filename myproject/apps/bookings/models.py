from django.db import models
from django.conf import settings
from apps.rooms.models import Room


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='bookings',
        null=True,
        blank=True
    )
    booking_ref = models.CharField(max_length=50, unique=True, editable=False)
    check_in = models.DateField()
    checkin_time = models.TimeField(default="14:00:00", help_text="Check-in time, default 2:00 PM")
    check_out = models.DateField()
    checkout_time = models.TimeField(default="11:00:00", help_text="Checkout time, default 11:00 AM")
    estimated_arrival_time = models.TimeField(null=True, blank=True, help_text="Estimated time of arrival")
    guest_count = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    is_featured = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'bookings'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['booking_ref']),
            models.Index(fields=['check_in', 'check_out']),
        ]

    def __str__(self):
        user_email = self.user.email if self.user else "Guest"
        return f"{self.booking_ref} — {user_email}"

    @property
    def nights(self):
        return (self.check_out - self.check_in).days


class BookingRoom(models.Model):
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='booking_rooms'
    )
    room = models.ForeignKey(
        Room,
        on_delete=models.PROTECT,
        related_name='bookingroom_set'
    )
    price_snapshot = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Room price per night at the time of booking"
    )

    class Meta:
        db_table = 'booking_rooms'
        indexes = [
            models.Index(fields=['booking']),
            models.Index(fields=['room']),
        ]