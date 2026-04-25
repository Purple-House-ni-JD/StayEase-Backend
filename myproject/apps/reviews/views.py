from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated

from core.permissions import IsOwnerOrAdmin
from .models import Review
from .serializers import ReviewSerializer


class ReviewListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/reviews/?room=<id>  — public
    POST /api/v1/reviews/            — authenticated guests
    """
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filterset_fields = ['room']
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']

    def get_queryset(self):
        return Review.objects.select_related('user', 'room').all()


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    """PATCH/DELETE /api/v1/reviews/{id}/ — owner only."""
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    http_method_names = ['get', 'patch', 'delete']

    def get_queryset(self):
        return Review.objects.select_related('user', 'room').all()