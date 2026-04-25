from django.contrib import admin
from .models import Room, Amenity, Policy, RoomAmenity, RoomPolicy


class RoomAmenityInline(admin.TabularInline):
    model = RoomAmenity
    extra = 1


class RoomPolicyInline(admin.TabularInline):
    model = RoomPolicy
    extra = 1


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price_per_night', 'max_guest', 'rating',
                    'availability_status', 'is_featured', 'created_at']
    list_filter = ['category', 'availability_status', 'is_featured']
    search_fields = ['name', 'description']
    inlines = [RoomAmenityInline, RoomPolicyInline]


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon']


@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
    list_display = ['title', 'type']