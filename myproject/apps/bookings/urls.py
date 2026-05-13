from django.urls import path
from .views import (
    BookingListAdminView, MyBookingsView, BookingCreateView,
    GuestBookingCreateView, BookingDetailView, BookingStatusUpdateView, BookingCancelView, RoomBookedDatesView
)

urlpatterns = [
    path('', BookingListAdminView.as_view(), name='booking-list'),
    path('create/', BookingCreateView.as_view(), name='booking-create'),
    path('guest/create/', GuestBookingCreateView.as_view(), name='guest-booking-create'),
    path('my/', MyBookingsView.as_view(), name='booking-my'),
    path('<int:pk>/', BookingDetailView.as_view(), name='booking-detail'),
    path('<int:pk>/status/', BookingStatusUpdateView.as_view(), name='booking-status'),
    path('<int:pk>/cancel/', BookingCancelView.as_view(), name='booking-cancel'),
    path('<int:pk>/booked-dates/', RoomBookedDatesView.as_view(), name='room-booked-dates'),
]