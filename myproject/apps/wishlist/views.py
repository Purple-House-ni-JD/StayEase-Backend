from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Wishlist
from .serializers import WishlistSerializer


class WishlistListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/wishlist/ — authenticated user's saved rooms
    POST /api/v1/wishlist/ — add a room to wishlist
    """
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user).select_related('room')


class WishlistDeleteView(APIView):
    """DELETE /api/v1/wishlist/{room_id}/ — remove room from wishlist."""
    permission_classes = [IsAuthenticated]

    def delete(self, request, room_id):
        deleted, _ = Wishlist.objects.filter(
            user=request.user,
            room_id=room_id
        ).delete()

        if not deleted:
            return Response({'detail': 'Room not found in wishlist.'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'detail': 'Removed from wishlist.'}, status=status.HTTP_204_NO_CONTENT)