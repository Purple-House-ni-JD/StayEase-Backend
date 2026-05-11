from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('apps.users.urls')),
    path('api/v1/users/', include('apps.users.urls')),
    path('api/v1/rooms/', include('apps.rooms.urls')),
    path('api/v1/bookings/', include('apps.bookings.urls')),
    path('api/v1/payments/', include('apps.payments.urls')),
    path('api/v1/reviews/', include('apps.reviews.urls')),
    path('api/v1/wishlist/', include('apps.wishlist.urls')),
    path('api/v1/reports/', include('apps.reports.urls')),
    path('api/v1/amenities/', include('apps.rooms.amenity_urls')),
    path('api/v1/policies/', include('apps.rooms.policy_urls')),
]