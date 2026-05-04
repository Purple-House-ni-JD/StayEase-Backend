from rest_framework import serializers
from django.db import transaction
from django.utils import timezone

from core.utils import generate_booking_ref, calculate_nights
from apps.rooms.models import Room
from apps.rooms.serializers import RoomListSerializer
from apps.payments.models import Payment
from .models import Booking, BookingRoom


class BookingRoomSerializer(serializers.ModelSerializer):
    room = RoomListSerializer(read_only=True)

    class Meta:
        model = BookingRoom
        fields = ['id', 'room', 'price_snapshot']


class BookingListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""
    user_email = serializers.EmailField(source='user.email', read_only=True)
    nights = serializers.IntegerField(read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'booking_ref', 'user_email', 'check_in', 'check_out',
            'nights', 'guest_count', 'total_price', 'status', 'created_at',
        ]


class BookingDetailSerializer(serializers.ModelSerializer):
    """Full booking detail including rooms and payment."""
    booking_rooms = BookingRoomSerializer(many=True, read_only=True)
    nights = serializers.IntegerField(read_only=True)
    payment_status = serializers.SerializerMethodField()
    payment_method = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            'id', 'booking_ref', 'check_in', 'check_out', 'nights',
            'guest_count', 'total_price', 'status', 'is_featured',
            'booking_rooms', 'payment_status', 'payment_method', 'created_at',
        ]

    def get_payment_status(self, obj):
        payment = getattr(obj, 'payment', None)
        return payment.status if payment else None

    def get_payment_method(self, obj):
        payment = getattr(obj, 'payment', None)
        return payment.method if payment else None


class BookingCreateSerializer(serializers.Serializer):
    """Handles the full booking creation flow."""
    room_ids = serializers.ListField(
        child=serializers.IntegerField(), min_length=1
    )
    check_in = serializers.DateField()
    check_out = serializers.DateField()
    guest_count = serializers.IntegerField(min_value=1)
    payment_method = serializers.ChoiceField(choices=Payment.METHOD_CHOICES)
    guest_details = serializers.DictField(required=False, write_only=True)

    def validate(self, attrs):
        check_in = attrs['check_in']
        check_out = attrs['check_out']
        today = timezone.now().date()

        if check_in < today:
            raise serializers.ValidationError({'check_in': 'Check-in cannot be in the past.'})
        if check_out <= check_in:
            raise serializers.ValidationError({'check_out': 'Check-out must be after check-in.'})

        # Validate all rooms exist and are available
        room_ids = attrs['room_ids']
        rooms = Room.objects.filter(id__in=room_ids, availability_status=True)
        if rooms.count() != len(set(room_ids)):
            raise serializers.ValidationError(
                {'room_ids': 'One or more rooms are unavailable or do not exist.'}
            )

        # Check date conflicts for each room
        conflicting = Room.objects.filter(
            id__in=room_ids,
            bookingroom_set__booking__status__in=['pending', 'confirmed'],
            bookingroom_set__booking__check_in__lt=check_out,
            bookingroom_set__booking__check_out__gt=check_in,
        ).distinct()

        if conflicting.exists():
            names = list(conflicting.values_list('name', flat=True))
            raise serializers.ValidationError(
                {'room_ids': f'Rooms already booked for these dates: {names}'}
            )

        attrs['rooms'] = rooms
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        # Get user from request context (will be None for guest bookings)
        user = getattr(self.context['request'], 'user', None) if self.context['request'].user.is_authenticated else None
        rooms = validated_data['rooms']
        check_in = validated_data['check_in']
        check_out = validated_data['check_out']
        nights = calculate_nights(check_in, check_out)
        guest_details = validated_data.pop('guest_details', None)

        # Calculate total price
        total_price = sum(room.price_per_night * nights for room in rooms)

        # Create booking
        booking = Booking.objects.create(
            user=user,
            booking_ref=generate_booking_ref(),
            check_in=check_in,
            check_out=check_out,
            guest_count=validated_data['guest_count'],
            total_price=total_price,
            status='pending',
        )

        # Store guest details if provided
        if guest_details and not user:
            # You could add guest_details fields to the Booking model if needed
            # For now, we'll just pass the booking through
            pass

        # Create BookingRoom rows (snapshot price)
        for room in rooms:
            BookingRoom.objects.create(
                booking=booking,
                room=room,
                price_snapshot=room.price_per_night,
            )

        # Create Payment record
        Payment.objects.create(
            booking=booking,
            amount=total_price,
            method=validated_data['payment_method'],
            status='pending',
        )

        return booking


class BookingStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['status']

    def validate_status(self, value):
        allowed = ['confirmed', 'cancelled', 'completed']
        if value not in allowed:
            raise serializers.ValidationError(f"Status must be one of: {allowed}")
        return value