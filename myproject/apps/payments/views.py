from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated

from core.permissions import IsAdmin
from .models import Payment
from .serializers import PaymentSerializer, PaymentStatusUpdateSerializer


class PaymentDetailView(generics.RetrieveAPIView):
    """GET /api/v1/payments/{booking_id}/ — Owner or admin."""
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'booking_id'

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Payment.objects.select_related('booking').all()
        return Payment.objects.select_related('booking').filter(booking__user=user)


class GuestPaymentDetailView(generics.RetrieveAPIView):
    """GET /api/v1/payments/guest/{booking_id}/ — Guest access to payment details."""
    serializer_class = PaymentSerializer
    permission_classes = [AllowAny]
    lookup_field = 'booking_id'

    def get_queryset(self):
        # Only allow access to payments for bookings without a user (guest bookings)
        return Payment.objects.select_related('booking').filter(booking__user__isnull=True)


class PaymentUpdateView(generics.UpdateAPIView):
    """PATCH /api/v1/payments/{booking_id}/ — Admin: update payment status."""
    serializer_class = PaymentStatusUpdateSerializer
    permission_classes = [IsAdmin]
    lookup_field = 'booking_id'
    http_method_names = ['patch']

    def get_queryset(self):
        return Payment.objects.all()