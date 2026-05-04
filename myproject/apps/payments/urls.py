from django.urls import path
from .views import PaymentDetailView, GuestPaymentDetailView, PaymentUpdateView

urlpatterns = [
    path('<int:booking_id>/', PaymentDetailView.as_view(), name='payment-detail'),
    path('guest/<int:booking_id>/', GuestPaymentDetailView.as_view(), name='guest-payment-detail'),
    path('<int:booking_id>/update/', PaymentUpdateView.as_view(), name='payment-update'),
]