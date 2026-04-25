from django.db import models
from django.conf import settings
from apps.rooms.models import Room


class Wishlist(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wishlist'
    )
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='wishlisted_by')
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'wishlist'
        unique_together = [('user', 'room')]

    def __str__(self):
        return f"{self.user.email} → {self.room.name}"