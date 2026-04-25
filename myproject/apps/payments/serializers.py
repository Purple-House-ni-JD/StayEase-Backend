from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    booking_ref = serializers.CharField(source='booking.booking_ref', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'booking_ref', 'amount', 'method',
            'status', 'transaction_ref', 'paid_at',
        ]
        read_only_fields = ['id', 'booking_ref', 'amount']


class PaymentStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['status', 'transaction_ref', 'paid_at']