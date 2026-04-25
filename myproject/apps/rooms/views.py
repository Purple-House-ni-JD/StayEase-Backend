import cloudinary.uploader
from rest_framework import generics, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from core.permissions import IsAdminOrReadOnly
from .filters import RoomFilter
from .models import Room, Amenity, Policy
from .serializers import (
    RoomListSerializer, RoomDetailSerializer,
    RoomImageUploadSerializer, RoomImageDeleteSerializer,
    AmenitySerializer, PolicySerializer,
)


class RoomViewSet(ModelViewSet):
    """
    list:   GET  /api/v1/rooms/           — public, filterable
    create: POST /api/v1/rooms/           — admin only
    retrieve: GET /api/v1/rooms/{id}/     — public
    update: PATCH /api/v1/rooms/{id}/     — admin only
    destroy: DELETE /api/v1/rooms/{id}/   — admin only
    """
    queryset = Room.objects.prefetch_related('amenities', 'policies').all()
    permission_classes = [IsAdminOrReadOnly]
    filterset_class = RoomFilter
    search_fields = ['name', 'description', 'category']
    ordering_fields = ['price_per_night', 'rating', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return RoomListSerializer
        return RoomDetailSerializer

    @action(detail=False, methods=['get'], url_path='featured', permission_classes=[AllowAny])
    def featured(self, request):
        rooms = self.get_queryset().filter(is_featured=True, availability_status=True)
        serializer = RoomListSerializer(rooms, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='categories', permission_classes=[AllowAny])
    def categories(self, request):
        choices = [{'value': k, 'label': v} for k, v in Room.CATEGORY_CHOICES]
        return Response(choices)

    @action(detail=True, methods=['post'], url_path='images',
            permission_classes=[IsAuthenticated])
    def upload_images(self, request, pk=None):
        from core.permissions import IsAdmin
        if not IsAdmin().has_permission(request, self):
            return Response({'detail': 'Admin only.'}, status=status.HTTP_403_FORBIDDEN)

        room = self.get_object()
        serializer = RoomImageUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uploaded_urls = []
        for image in serializer.validated_data['images']:
            result = cloudinary.uploader.upload(
                image,
                folder=f'stayease/rooms/{room.id}',
                resource_type='image',
            )
            uploaded_urls.append(result['secure_url'])

        room.image_urls = (room.image_urls or []) + uploaded_urls
        room.save(update_fields=['image_urls'])
        return Response({'image_urls': room.image_urls}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['delete'], url_path='images/remove',
            permission_classes=[IsAuthenticated])
    def remove_image(self, request, pk=None):
        from core.permissions import IsAdmin
        if not IsAdmin().has_permission(request, self):
            return Response({'detail': 'Admin only.'}, status=status.HTTP_403_FORBIDDEN)

        room = self.get_object()
        serializer = RoomImageDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        url = serializer.validated_data['url']
        if url not in (room.image_urls or []):
            return Response({'detail': 'URL not found.'}, status=status.HTTP_404_NOT_FOUND)

        room.image_urls.remove(url)
        room.save(update_fields=['image_urls'])
        return Response({'image_urls': room.image_urls}, status=status.HTTP_200_OK)


# --- Amenity & Policy views ---

class AmenityListCreateView(generics.ListCreateAPIView):
    queryset = Amenity.objects.all()
    serializer_class = AmenitySerializer
    permission_classes = [IsAdminOrReadOnly]


class AmenityDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Amenity.objects.all()
    serializer_class = AmenitySerializer
    permission_classes = [IsAdminOrReadOnly]


class PolicyListCreateView(generics.ListCreateAPIView):
    queryset = Policy.objects.all()
    serializer_class = PolicySerializer
    permission_classes = [IsAdminOrReadOnly]


class PolicyDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Policy.objects.all()
    serializer_class = PolicySerializer
    permission_classes = [IsAdminOrReadOnly]