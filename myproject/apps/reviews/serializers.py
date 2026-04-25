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