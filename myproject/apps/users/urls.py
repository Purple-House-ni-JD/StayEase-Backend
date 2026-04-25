from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    LoginView, RegisterView, LogoutView, MeView, AvatarUploadView,
    GoogleOAuthView, FacebookOAuthView,
)

urlpatterns = [
    # Standard email/password
    path('register/', RegisterView.as_view(), name='auth-register'),
    path('login/', LoginView.as_view(), name='auth-login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('logout/', LogoutView.as_view(), name='auth-logout'),

    # Profile
    path('me/', MeView.as_view(), name='auth-me'),
    path('me/avatar/', AvatarUploadView.as_view(), name='auth-avatar'),

    # OAuth
    path('oauth/google/', GoogleOAuthView.as_view(), name='auth-google'),
    path('oauth/facebook/', FacebookOAuthView.as_view(), name='auth-facebook'),
]