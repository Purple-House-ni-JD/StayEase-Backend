from rest_framework import serializers
from .models import Room, Amenity, Policy, RoomAmenity, RoomPolicy


class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = ['id', 'name', 'icon']


class PolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = Policy
        fields = ['id', 'type', 'title', 'description']


class RoomListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""
    category_display = serializers.CharField(source='get_category_display', read_only=True)

    class Meta:
        model = Room
        fields = [
            'id', 'name', 'category', 'category_display',
            'price_per_night', 'max_guest', 'rating',
            'image_urls', 'availability_status', 'is_featured',
        ]


class RoomDetailSerializer(serializers.ModelSerializer):
    """Full serializer including amenities and policies."""
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    amenities = AmenitySerializer(many=True, read_only=True)
    policies = PolicySerializer(many=True, read_only=True)
    amenity_ids = serializers.PrimaryKeyRelatedField(
        queryset=Amenity.objects.all(), many=True, write_only=True,
        source='amenities', required=False
    )
    policy_ids = serializers.PrimaryKeyRelatedField(
        queryset=Policy.objects.all(), many=True, write_only=True,
        source='policies', required=False
    )

    class Meta:
        model = Room
        fields = [
            'id', 'name', 'category', 'category_display', 'description',
            'price_per_night', 'max_guest', 'rating',
            'image_urls', 'availability_status', 'is_featured',
            'amenities', 'amenity_ids',
            'policies', 'policy_ids',
            'created_at',
        ]
        read_only_fields = ['id', 'rating', 'created_at']

    def create(self, validated_data):
        amenities = validated_data.pop('amenities', [])
        policies = validated_data.pop('policies', [])
        room = Room.objects.create(**validated_data)
        room.amenities.set(amenities)
        room.policies.set(policies)
        return room

    def update(self, instance, validated_data):
        amenities = validated_data.pop('amenities', None)
        policies = validated_data.pop('policies', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if amenities is not None:
            instance.amenities.set(amenities)
        if policies is not None:
            instance.policies.set(policies)
        return instance


class RoomImageUploadSerializer(serializers.Serializer):
    images = serializers.ListField(
        child=serializers.ImageField(),
        allow_empty=False,
        max_length=10,
    )


class RoomImageDeleteSerializer(serializers.Serializer):
    url = serializers.URLField()