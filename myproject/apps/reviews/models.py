from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.rooms.models import Room
from apps.bookings.models import Booking


class Review(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='reviews')
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField()
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'reviews'
        unique_together = [('user', 'booking')]  # one review per booking

    def __str__(self):
        return f"Review by {self.user.email} for {self.room.name} — {self.rating}★"