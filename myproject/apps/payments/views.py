from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

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


class PaymentUpdateView(generics.UpdateAPIView):
    """PATCH /api/v1/payments/{booking_id}/ — Admin: update payment status."""
    serializer_class = PaymentStatusUpdateSerializer
    permission_classes = [IsAdmin]
    lookup_field = 'booking_id'
    http_method_names = ['patch']

    def get_queryset(self):
        return Payment.objects.all()