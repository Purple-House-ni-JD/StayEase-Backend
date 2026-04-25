from django.urls import path
from .views import PaymentDetailView, PaymentUpdateView

urlpatterns = [
    path('<int:booking_id>/', PaymentDetailView.as_view(), name='payment-detail'),
    path('<int:booking_id>/update/', PaymentUpdateView.as_view(), name='payment-update'),
]