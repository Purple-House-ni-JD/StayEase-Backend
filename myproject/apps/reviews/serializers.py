from rest_framework import serializers
from apps.bookings.models import Booking
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    room_name = serializers.CharField(source='room.name', read_only=True)

    class Meta:
        model = Review
        fields = [
            'id', 'user_name', 'room', 'room_name', 'booking',
            'rating', 'comment', 'created_at',
        ]
        read_only_fields = ['id', 'user_name', 'room_name', 'created_at']

    def validate_rating(self, value):
        if not isinstance(value, int) or not (1 <= value <= 5):
            raise serializers.ValidationError("Rating must be an integer between 1 and 5.")
        return value

    def validate_comment(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Comment cannot be empty.")
        return value.strip()

    def get_user_name(self, obj):
        return obj.user.get_full_name() or obj.user.email

    def validate(self, attrs):
        request = self.context['request']
        booking = attrs.get('booking')
        room = attrs.get('room')

        # Ensure the booking belongs to the requesting user
        if booking.user != request.user:
            raise serializers.ValidationError(
                {'booking': 'You can only review your own bookings.'}
            )

        # Ensure the booking includes the room being reviewed
        if not booking.booking_rooms.filter(room=room).exists():
            raise serializers.ValidationError(
                {'room': 'This room was not part of the specified booking.'}
            )

        # Ensure booking is completed
        if booking.status != 'completed':
            raise serializers.ValidationError(
                {'booking': 'You can only review completed bookings.'}
            )

        # Check if user has already reviewed this booking
        if Review.objects.filter(user=request.user, booking=booking).exists():
            raise serializers.ValidationError(
                {'booking': 'You have already submitted a review for this booking. Only one review is allowed per booking.'}
            )

        return attrs

    def create(self, validated_data):
        review = Review.objects.create(
            user=self.context['request'].user,
            **validated_data
        )
        # Update room's average rating
        self._update_room_rating(review.room)
        return review

    def _update_room_rating(self, room):
        from django.db.models import Avg
        avg = Review.objects.filter(room=room).aggregate(avg=Avg('rating'))['avg']
        room.rating = round(avg or 0, 2)
        room.save(update_fields=['rating'])