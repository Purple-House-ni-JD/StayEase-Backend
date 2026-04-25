"""
OAuth token verification services.

Flow (React Native side):
  1. User taps "Sign in with Google/Facebook"
  2. Expo / native SDK runs the OAuth flow and returns a token
  3. App POSTs that token to our backend endpoint
  4. We verify the token with the provider, extract user info
  5. We find-or-create the User + OAuthAccount
  6. We return our own JWT pair

Google  → send the id_token  (JWT signed by Google)
Facebook → send the access_token from Facebook SDK
"""

import logging
import urllib.request
import json
from typing import TypedDict

import requests
from django.db import transaction

from .models import User, OAuthAccount

logger = logging.getLogger(__name__)

GOOGLE_TOKEN_INFO_URL = 'https://oauth2.googleapis.com/tokeninfo'
FACEBOOK_GRAPH_URL = 'https://graph.facebook.com/me'


# ---------------------------------------------------------------------------
# Typed dicts for verified provider payloads
# ---------------------------------------------------------------------------

class ProviderPayload(TypedDict):
    provider_user_id: str
    email: str
    first_name: str
    last_name: str
    avatar_url: str


# ---------------------------------------------------------------------------
# Google
# ---------------------------------------------------------------------------

def verify_google_token(id_token: str) -> ProviderPayload:
    """
    Verify a Google ID token by calling Google's tokeninfo endpoint.
    Returns structured user data on success, raises ValueError on failure.

    The React Native app should use expo-auth-session or
    @react-native-google-signin/google-signin to obtain the id_token.
    """
    try:
        resp = requests.get(
            GOOGLE_TOKEN_INFO_URL,
            params={'id_token': id_token},
            timeout=10,
        )
        resp.raise_for_status()
        payload = resp.json()
    except requests.RequestException as e:
        logger.error("Google token verification request failed: %s", e)
        raise ValueError("Could not reach Google to verify token.")

    if 'error' in payload or 'error_description' in payload:
        raise ValueError(f"Invalid Google token: {payload.get('error_description', 'unknown error')}")

    # Required fields
    provider_user_id = payload.get('sub')
    email = payload.get('email')
    if not provider_user_id or not email:
        raise ValueError("Google token missing required fields (sub, email).")

    if payload.get('email_verified') != 'true':
        raise ValueError("Google account email is not verified.")

    # Extract name — Google may provide given_name / family_name or just name
    name_parts = payload.get('name', '').split(' ', 1)
    first_name = payload.get('given_name') or (name_parts[0] if name_parts else '')
    last_name = payload.get('family_name') or (name_parts[1] if len(name_parts) > 1 else '')

    return ProviderPayload(
        provider_user_id=provider_user_id,
        email=email,
        first_name=first_name,
        last_name=last_name,
        avatar_url=payload.get('picture', ''),
    )


# ---------------------------------------------------------------------------
# Facebook
# ---------------------------------------------------------------------------

def verify_facebook_token(access_token: str) -> ProviderPayload:
    """
    Verify a Facebook user access token by calling the Graph API.
    Returns structured user data on success, raises ValueError on failure.

    The React Native app should use react-native-fbsdk-next or
    expo-facebook to obtain the access_token.

    Required Facebook app permissions: public_profile, email
    """
    try:
        resp = requests.get(
            FACEBOOK_GRAPH_URL,
            params={
                'fields': 'id,email,first_name,last_name,picture.type(large)',
                'access_token': access_token,
            },
            timeout=10,
        )
        resp.raise_for_status()
        payload = resp.json()
    except requests.RequestException as e:
        logger.error("Facebook token verification request failed: %s", e)
        raise ValueError("Could not reach Facebook to verify token.")

    if 'error' in payload:
        err = payload['error']
        raise ValueError(f"Invalid Facebook token: {err.get('message', 'unknown error')}")

    provider_user_id = payload.get('id')
    email = payload.get('email')

    if not provider_user_id:
        raise ValueError("Facebook token missing required field (id).")

    if not email:
        # Facebook may not return email if user hasn't granted permission
        # or uses a phone-number-only account
        raise ValueError(
            "Facebook did not return an email address. "
            "Please ensure the app has 'email' permission and the account has an email."
        )

    avatar_url = ''
    picture = payload.get('picture', {})
    if isinstance(picture, dict):
        avatar_url = picture.get('data', {}).get('url', '')

    return ProviderPayload(
        provider_user_id=provider_user_id,
        email=email,
        first_name=payload.get('first_name', ''),
        last_name=payload.get('last_name', ''),
        avatar_url=avatar_url,
    )


# ---------------------------------------------------------------------------
# Find-or-create user
# ---------------------------------------------------------------------------

@transaction.atomic
def get_or_create_oauth_user(provider: str, payload: ProviderPayload) -> tuple[User, bool]:
    """
    Given a verified provider payload, find or create the User and OAuthAccount.

    Returns (user, created) where created=True means a new account was made.

    Logic:
      1. If OAuthAccount already exists → return its user (returning user)
      2. If a User with the same email exists → link this provider to it
      3. Otherwise → create a new User + OAuthAccount
    """
    # Case 1: existing OAuth link
    try:
        oauth_account = OAuthAccount.objects.select_related('user').get(
            provider=provider,
            provider_user_id=payload['provider_user_id'],
        )
        # Update avatar from provider if user hasn't set their own
        user = oauth_account.user
        if payload['avatar_url'] and not user.avatar_url:
            user.avatar_url = payload['avatar_url']
            user.save(update_fields=['avatar_url'])
        return user, False
    except OAuthAccount.DoesNotExist:
        pass

    # Case 2: user with same email already exists (e.g. registered via password)
    user = None
    created = False
    try:
        user = User.objects.get(email=payload['email'])
    except User.DoesNotExist:
        # Case 3: brand new user
        username = _unique_username(payload['email'])
        user = User.objects.create_user(
            email=payload['email'],
            username=username,
            first_name=payload['first_name'],
            last_name=payload['last_name'],
            avatar_url=payload['avatar_url'],
            role='guest',
        )
        # OAuth users have no password — set unusable
        user.set_unusable_password()
        user.save(update_fields=['password'])
        created = True

    # Create the OAuth link
    OAuthAccount.objects.create(
        user=user,
        provider=provider,
        provider_user_id=payload['provider_user_id'],
        provider_avatar_url=payload['avatar_url'],
    )

    # Backfill avatar on existing user if they don't have one
    if payload['avatar_url'] and not user.avatar_url:
        user.avatar_url = payload['avatar_url']
        user.save(update_fields=['avatar_url'])

    return user, created


def _unique_username(email: str) -> str:
    """Derive a unique username from an email address."""
    base = email.split('@')[0]
    username = base
    counter = 1
    while User.objects.filter(username=username).exists():
        username = f"{base}{counter}"
        counter += 1
    return username