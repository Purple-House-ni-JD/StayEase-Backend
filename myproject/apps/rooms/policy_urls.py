from django.urls import path
from .views import PolicyListCreateView, PolicyDetailView

urlpatterns = [
    path('', PolicyListCreateView.as_view(), name='policy-list'),
    path('<int:pk>/', PolicyDetailView.as_view(), name='policy-detail'),
]