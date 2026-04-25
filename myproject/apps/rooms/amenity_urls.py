from django.urls import path
from .views import AmenityListCreateView, AmenityDetailView

urlpatterns = [
    path('', AmenityListCreateView.as_view(), name='amenity-list'),
    path('<int:pk>/', AmenityDetailView.as_view(), name='amenity-detail'),
]