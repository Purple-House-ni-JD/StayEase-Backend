from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import IsAdmin
from .services import revenue_report, occupancy_report, top_rooms_report, dashboard_summary


class DashboardSummaryView(APIView):
    """GET /api/v1/reports/dashboard/ — Admin summary cards."""
    permission_classes = [IsAdmin]

    def get(self, request):
        return Response(dashboard_summary())


class RevenueReportView(APIView):
    """
    GET /api/v1/reports/revenue/
    Query params:
      period = daily | weekly | monthly  (default: monthly)
      year   = YYYY
      month  = MM
    """
    permission_classes = [IsAdmin]

    def get(self, request):
        period = request.query_params.get('period', 'monthly')
        if period not in ('daily', 'weekly', 'monthly'):
            return Response({'detail': 'period must be daily, weekly, or monthly.'}, status=400)

        year = request.query_params.get('year')
        month = request.query_params.get('month')

        try:
            year = int(year) if year else None
            month = int(month) if month else None
        except ValueError:
            return Response({'detail': 'year and month must be integers.'}, status=400)

        data = revenue_report(period=period, year=year, month=month)
        return Response({'period': period, 'results': data})


class OccupancyReportView(APIView):
    """
    GET /api/v1/reports/occupancy/
    Query params:
      period = daily | weekly | monthly  (default: monthly)
    """
    permission_classes = [IsAdmin]

    def get(self, request):
        period = request.query_params.get('period', 'monthly')
        if period not in ('daily', 'weekly', 'monthly'):
            return Response({'detail': 'period must be daily, weekly, or monthly.'}, status=400)

        data = occupancy_report(period=period)
        return Response({'period': period, 'results': data})


class TopRoomsReportView(APIView):
    """
    GET /api/v1/reports/top-rooms/
    Query params:
      order_by = revenue | bookings  (default: revenue)
      limit    = int                 (default: 10)
    """
    permission_classes = [IsAdmin]

    def get(self, request):
        order_by = request.query_params.get('order_by', 'revenue')
        if order_by not in ('revenue', 'bookings'):
            return Response({'detail': 'order_by must be revenue or bookings.'}, status=400)

        try:
            limit = int(request.query_params.get('limit', 10))
            limit = max(1, min(limit, 50))  # clamp between 1 and 50
        except ValueError:
            return Response({'detail': 'limit must be an integer.'}, status=400)

        data = top_rooms_report(limit=limit, order_by=order_by)
        return Response({'order_by': order_by, 'results': data})