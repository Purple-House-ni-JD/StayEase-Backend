from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import User, OAuthAccount


class OAuthAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = OAuthAccount
        fields = ['provider', 'created_at']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, label='Confirm password')

    class Meta:
        model = User
        fields = [
            'email', 'username', 'first_name', 'last_name',
            'phone_number', 'password', 'password2',
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password2'):
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data.get('username', validated_data['email']),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone_number=validated_data.get('phone_number', ''),
            password=validated_data['password'],
            role='guest',
        )
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    has_password = serializers.BooleanField(read_only=True)
    linked_providers = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'phone_number', 'avatar_url', 'role', 'date_joined',
            'has_password', 'linked_providers',
            'is_staff', 'is_superuser', # <-- ADDED THESE TWO
        ]
        read_only_fields = [
            'id', 'email', 'role', 'date_joined', 
            'has_password', 'linked_providers',
            'is_staff', 'is_superuser', # <-- ADDED HERE TOO
        ]

    def get_linked_providers(self, obj):
        return list(obj.oauth_accounts.values_list('provider', flat=True))


class AvatarUploadSerializer(serializers.Serializer):
    avatar = serializers.ImageField()


# ---------------------------------------------------------------------------
# OAuth serializers
# ---------------------------------------------------------------------------

class GoogleOAuthSerializer(serializers.Serializer):
    """
    Accepts the id_token from Google Sign-In on the mobile app.
    React Native: obtain via expo-auth-session or @react-native-google-signin/google-signin
    """
    id_token = serializers.CharField(
        help_text="The ID token returned by Google Sign-In on the mobile client."
    )


class FacebookOAuthSerializer(serializers.Serializer):
    """
    Accepts the access_token from Facebook Login on the mobile app.
    React Native: obtain via react-native-fbsdk-next or expo-facebook
    """
    access_token = serializers.CharField(
        help_text="The user access token returned by Facebook Login on the mobile client."
    )