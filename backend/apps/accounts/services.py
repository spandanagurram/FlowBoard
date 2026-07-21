from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError, transaction
from django.utils.encoding import force_str
from django.utils.http import base36_to_int, urlsafe_base64_decode, urlsafe_base64_encode
from google.auth import exceptions as google_auth_exceptions
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import UserSerializer


User = get_user_model()


class PasswordResetService:
    token_generator = PasswordResetTokenGenerator()

    @staticmethod
    def send_reset_email(email):
        user = User.objects.filter(email__iexact=email, is_active=True).first()
        if user is None:
            return

        uid = urlsafe_base64_encode(force_str(user.pk).encode())
        token = PasswordResetService.token_generator.make_token(user)
        reset_url = f"{settings.FRONTEND_URL}/reset-password?uid={uid}&token={token}"

        from .tasks import send_password_reset_email

        send_password_reset_email.delay(user.email, reset_url)

    @staticmethod
    def validate_reset_request(*, uid, token, password):
        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id, is_active=True)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError({"uid": "Invalid user identifier."})

        if PasswordResetService._is_token_expired(token):
            raise serializers.ValidationError({"token": "Password reset token has expired."})

        if not PasswordResetService.token_generator.check_token(user, token):
            raise serializers.ValidationError({"token": "Invalid password reset token."})

        try:
            validate_password(password, user)
        except DjangoValidationError as error:
            raise serializers.ValidationError({"password": list(error.messages)})

        return user

    @staticmethod
    def reset_password(*, user, password):
        user.set_password(password)
        user.save()

    @staticmethod
    def _is_token_expired(token):
        try:
            timestamp = base36_to_int(token.split("-", 1)[0])
        except (ValueError, IndexError):
            return False

        return (
            PasswordResetService.token_generator._num_seconds(
                PasswordResetService.token_generator._now()
            )
            - timestamp
            > settings.PASSWORD_RESET_TIMEOUT
        )


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
