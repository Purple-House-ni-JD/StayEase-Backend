from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('guest', 'Guest'),
        ('admin', 'Admin'),
    ]

    # Make email the login field
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True)
    avatar_url = models.TextField(blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='guest')

    USERNAME_FIELD = 'email'
    # username is still required by AbstractUser; we keep it but don't use it for login
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
        ]

    def __str__(self):
        return f"{self.get_full_name()} <{self.email}>"

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def has_password(self):
        """False for OAuth-only accounts that have no usable password set."""
        return self.has_usable_password()


class OAuthAccount(models.Model):
    """
    Stores the link between a StayEase user and their OAuth provider account.
    A single user can have multiple providers (e.g. Google + Facebook).
    """
    PROVIDER_CHOICES = [
        ('google', 'Google'),
        ('facebook', 'Facebook'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='oauth_accounts'
    )
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    # The unique user ID from the provider (Google sub / Facebook id)
    provider_user_id = models.CharField(max_length=255)
    # Optional: store the provider's avatar URL for fallback
    provider_avatar_url = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'oauth_accounts'
        # One account per provider per user
        unique_together = [('provider', 'provider_user_id')]
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['provider']),
        ]

    def __str__(self):
        return f"{self.user.email} via {self.provider}"