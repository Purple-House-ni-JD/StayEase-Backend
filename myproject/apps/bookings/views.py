from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import IsAdmin, IsOwnerOrAdmin
from .models import Booking
from .serializers import (
    BookingListSerializer, BookingDetailSerializer,
    BookingCreateSerializer, BookingStatusUpdateSerializer,
)


class BookingListAdminView(generics.ListAPIView):
    """GET /api/v1/bookings/ — Admin: list all bookings."""
    serializer_class = BookingListSerializer
    permission_classes = [IsAdmin]
    filterset_fields = ['status', 'user']
    search_fields = ['booking_ref', 'user__email']
    ordering_fields = ['created_at', 'check_in', 'total_price']
    ordering = ['-created_at']

    def get_queryset(self):
        return Booking.objects.select_related('user').prefetch_related(
            'booking_rooms__room'
        ).all()


class MyBookingsView(generics.ListAPIView):
    """GET /api/v1/bookings/my/ — Guest: own bookings."""
    serializer_class = BookingListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).prefetch_related(
            'booking_rooms__room'
        )


class BookingCreateView(generics.CreateAPIView):
    """POST /api/v1/bookings/ — Guest: create a booking."""
    serializer_class = BookingCreateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = serializer.save()
        return Response(
            BookingDetailSerializer(booking).data,
            status=status.HTTP_201_CREATED
        )


class BookingDetailView(generics.RetrieveAPIView):
    """GET /api/v1/bookings/{id}/ — Owner or admin."""
    serializer_class = BookingDetailSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        return Booking.objects.select_related('user', 'payment').prefetch_related(
            'booking_rooms__room'
        )


class BookingStatusUpdateView(generics.UpdateAPIView):
    """PATCH /api/v1/bookings/{id}/status/ — Admin only."""
    serializer_class = BookingStatusUpdateSerializer
    permission_classes = [IsAdmin]
    http_method_names = ['patch']

    def get_queryset(self):
        return Booking.objects.all()

    def update(self, request, *args, **kwargs):
        booking = self.get_object()
        serializer = self.get_serializer(booking, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(BookingDetailSerializer(booking).data)


class BookingCancelView(APIView):
    """POST /api/v1/bookings/{id}/cancel/ — Guest self-cancel."""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            booking = Booking.objects.get(pk=pk, user=request.user)
        except Booking.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        if booking.status not in ['pending', 'confirmed']:
            return Response(
                {'detail': f'Cannot cancel a booking with status: {booking.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        booking.status = 'cancelled'
        booking.save(update_fields=['status'])
        return Response({'detail': 'Booking cancelled.', 'booking_ref': booking.booking_ref})