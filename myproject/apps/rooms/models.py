from django.db import models


class Amenity(models.Model):
    name = models.CharField(max_length=50)
    icon = models.CharField(max_length=50, help_text="Icon slug/name for frontend rendering")

    class Meta:
        db_table = 'amenities'
        verbose_name_plural = 'amenities'

    def __str__(self):
        return self.name


class Policy(models.Model):
    type = models.CharField(max_length=50, help_text="e.g. cancellation, check-in, pets")
    title = models.CharField(max_length=50)
    description = models.TextField()

    class Meta:
        db_table = 'policies'
        verbose_name_plural = 'policies'

    def __str__(self):
        return self.title


class Room(models.Model):
    CATEGORY_CHOICES = [
        ('standard', 'Standard'),
        ('deluxe', 'Deluxe'),
        ('superior', 'Superior'),
        ('junior_suite', 'Junior Suite'),
        ('executive_suite', 'Executive Suite'),
        ('family', 'Family'),
    ]

    name = models.CharField(max_length=50)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField()
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    max_guest = models.IntegerField()
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    image_urls = models.JSONField(default=list, blank=True)
    availability_status = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    amenities = models.ManyToManyField(Amenity, through='RoomAmenity', blank=True)
    policies = models.ManyToManyField(Policy, through='RoomPolicy', blank=True)
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'rooms'

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class RoomAmenity(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    amenity = models.ForeignKey(Amenity, on_delete=models.CASCADE)

    class Meta:
        db_table = 'room_amenities'
        unique_together = [('room', 'amenity')]


class RoomPolicy(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE)

    class Meta:
        db_table = 'room_policies'
        unique_together = [('room', 'policy')]