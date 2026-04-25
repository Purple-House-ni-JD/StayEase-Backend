from django.urls import path
from .views import WishlistListCreateView, WishlistDeleteView

urlpatterns = [
    path('', WishlistListCreateView.as_view(), name='wishlist-list'),
    path('<int:room_id>/', WishlistDeleteView.as_view(), name='wishlist-delete'),
]