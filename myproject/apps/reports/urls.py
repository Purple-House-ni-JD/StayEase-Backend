from django.urls import path
from .views import DashboardSummaryView, RevenueReportView, OccupancyReportView, TopRoomsReportView

urlpatterns = [
    path('dashboard/', DashboardSummaryView.as_view(), name='report-dashboard'),
    path('revenue/', RevenueReportView.as_view(), name='report-revenue'),
    path('occupancy/', OccupancyReportView.as_view(), name='report-occupancy'),
    path('top-rooms/', TopRoomsReportView.as_view(), name='report-top-rooms'),
]