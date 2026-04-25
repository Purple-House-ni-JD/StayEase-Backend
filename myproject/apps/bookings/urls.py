from django.urls import path
from .views import (
    BookingListAdminView, MyBookingsView, BookingCreateView,
    BookingDetailView, BookingStatusUpdateView, BookingCancelView,
)

urlpatterns = [
    path('', BookingListAdminView.as_view(), name='booking-list'),
    path('create/', BookingCreateView.as_view(), name='booking-create'),
    path('my/', MyBookingsView.as_view(), name='booking-my'),
    path('<int:pk>/', BookingDetailView.as_view(), name='booking-detail'),
    path('<int:pk>/status/', BookingStatusUpdateView.as_view(), name='booking-status'),
    path('<int:pk>/cancel/', BookingCancelView.as_view(), name='booking-cancel'),
]