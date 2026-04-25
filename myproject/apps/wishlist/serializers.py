from rest_framework import serializers
from apps.rooms.serializers import RoomListSerializer
from .models import Wishlist


class WishlistSerializer(serializers.ModelSerializer):
    room = RoomListSerializer(read_only=True)
    room_id = serializers.PrimaryKeyRelatedField(
        queryset=__import__('apps.rooms.models', fromlist=['Room']).Room.objects.all(),
        source='room',
        write_only=True
    )

    class Meta:
        model = Wishlist
        fields = ['id', 'room', 'room_id', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate(self, attrs):
        user = self.context['request'].user
        room = attrs['room']
        if Wishlist.objects.filter(user=user, room=room).exists():
            raise serializers.ValidationError({'room': 'This room is already in your wishlist.'})
        return attrs

    def create(self, validated_data):
        return Wishlist.objects.create(
            user=self.context['request'].user,
            **validated_data
        )