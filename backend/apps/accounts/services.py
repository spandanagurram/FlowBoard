from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from google.auth import exceptions as google_auth_exceptions
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import UserSerializer


User = get_user_model()


class GoogleAuthService:
    @staticmethod
    def login(id_token):
        google_user = GoogleAuthService._verify_id_token(id_token)
        email = google_user.get("email")

        if not email or google_user.get("email_verified") is not True:
            raise serializers.ValidationError(
                {"id_token": "Google did not provide a verified email address."}
            )

        with transaction.atomic():
            user = User.objects.select_for_update().filter(email__iexact=email).first()
            if user is None:
                user = GoogleAuthService._create_google_user(google_user)

            if not user.is_active or getattr(user, "is_deleted", False):
                raise serializers.ValidationError("This account has been disabled.")

        refresh = RefreshToken.for_user(user)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": UserSerializer(user).data,
        }

    @staticmethod
    def _verify_id_token(token):
        client_id = settings.GOOGLE_OAUTH_CLIENT_ID
        if not client_id:
            raise serializers.ValidationError("Google authentication is not configured.")

        try:
            # google-auth validates the token signature, audience, issuer, and expiry.
            return google_id_token.verify_oauth2_token(
                token,
                google_requests.Request(),
                client_id,
            )
        except (google_auth_exceptions.GoogleAuthError, ValueError):
            raise serializers.ValidationError({"id_token": "Invalid Google ID token."})

    @staticmethod
    def _create_google_user(google_user):
        email = google_user["email"]

        # Retry on a concurrent registration so the database remains the source of truth.
        while True:
            username = GoogleAuthService._generate_username(email)
            try:
                with transaction.atomic():
                    user = User(
                        email=email,
                        username=username,
                        first_name=google_user.get("given_name") or "",
                        last_name=google_user.get("family_name") or "",
                        auth_provider=User.AuthProvider.GOOGLE,
                    )
                    # Google users authenticate only with their Google account.
                    user.set_unusable_password()
                    user.save()
                    return user
            except IntegrityError:
                # Another request may have created this email or username first.
                existing_user = User.objects.filter(email__iexact=email).first()
                if existing_user:
                    return existing_user

    @staticmethod
    def _generate_username(email):
        base_username = email.split("@", 1)[0]
        username = base_username
        suffix = 1

        # Add an incrementing suffix until the username is unique.
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{suffix}"
            suffix += 1

        return username
