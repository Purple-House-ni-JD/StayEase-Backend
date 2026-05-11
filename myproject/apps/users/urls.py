from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    LoginView, RegisterView, LogoutView, MeView, AvatarUploadView,
    GoogleOAuthView, FacebookOAuthView, AdminUserListView, AdminUserDeleteView
)

# Auth endpoints (under /api/v1/auth/)
auth_urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth-register'),
    path('login/', LoginView.as_view(), name='auth-login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('logout/', LogoutView.as_view(), name='auth-logout'),
    path('me/', MeView.as_view(), name='auth-me'),
    path('me/avatar/', AvatarUploadView.as_view(), name='auth-avatar'),
    path('oauth/google/', GoogleOAuthView.as_view(), name='auth-google'),
    path('oauth/facebook/', FacebookOAuthView.as_view(), name='auth-facebook'),
]

# Admin user management endpoints (under /api/v1/users/)
admin_urlpatterns = [
    path('admin/list/', AdminUserListView.as_view(), name='admin-user-list'),
    path('admin/<int:pk>/delete/', AdminUserDeleteView.as_view(), name='admin-user-delete'),
]

urlpatterns = auth_urlpatterns + admin_urlpatterns