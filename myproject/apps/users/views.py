import cloudinary.uploader
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User
from .serializers import (
    RegisterSerializer, UserProfileSerializer, AvatarUploadSerializer,
    GoogleOAuthSerializer, FacebookOAuthSerializer,
)
from .oauth_services import (
    verify_google_token, verify_facebook_token,
    get_or_create_oauth_user,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _jwt_response(user: User, created: bool = False) -> Response:
    """Issue a JWT pair and return a standard auth response."""
    refresh = RefreshToken.for_user(user)
    http_status = status.HTTP_201_CREATED if created else status.HTTP_200_OK
    return Response({
        'user': UserProfileSerializer(user).data,
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }, status=http_status)


# ---------------------------------------------------------------------------
# Standard email/password auth
# ---------------------------------------------------------------------------

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Adds user info to the login response."""

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserProfileSerializer(self.user).data
        return data


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return _jwt_response(user, created=True)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response(
                    {'detail': 'Refresh token is required.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'detail': 'Successfully logged out.'}, status=status.HTTP_200_OK)
        except Exception:
            return Response({'detail': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class AvatarUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        serializer = AvatarUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        image_file = serializer.validated_data['avatar']
        result = cloudinary.uploader.upload(
            image_file,
            folder='stayease/avatars',
            public_id=f"user_{request.user.id}",
            overwrite=True,
            resource_type='image',
        )
        request.user.avatar_url = result['secure_url']
        request.user.save(update_fields=['avatar_url'])

        return Response({'avatar_url': request.user.avatar_url}, status=status.HTTP_200_OK)


# ---------------------------------------------------------------------------
# OAuth — Google
# ---------------------------------------------------------------------------

class GoogleOAuthView(APIView):
    """
    POST /api/v1/auth/oauth/google/

    Body: { "id_token": "<token from Google Sign-In>" }

    The React Native app should:
      1. Initialise Google Sign-In with your OAuth client ID
      2. Call signIn() → get the idToken from the result
      3. POST that idToken here

    Returns the same JWT pair as login/register.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = GoogleOAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            payload = verify_google_token(serializer.validated_data['id_token'])
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        user, created = get_or_create_oauth_user('google', payload)
        return _jwt_response(user, created=created)


# ---------------------------------------------------------------------------
# OAuth — Facebook
# ---------------------------------------------------------------------------

class FacebookOAuthView(APIView):
    """
    POST /api/v1/auth/oauth/facebook/

    Body: { "access_token": "<token from Facebook Login>" }

    The React Native app should:
      1. Call LoginManager.logInWithPermissions(['public_profile', 'email'])
      2. Get the token via AccessToken.getCurrentAccessToken()
      3. POST accessToken.tokenString here

    Returns the same JWT pair as login/register.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = FacebookOAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            payload = verify_facebook_token(serializer.validated_data['access_token'])
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        user, created = get_or_create_oauth_user('facebook', payload)
        return _jwt_response(user, created=created)