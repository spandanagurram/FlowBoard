from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken



User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        read_only_fields = ('id',)

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('A user with this email already exists.')
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = User.objects.filter(email__iexact=attrs['email']).first()
        if user is None:
            raise serializers.ValidationError('Invalid email or password.')

        authenticated_user = authenticate(
            request=self.context.get('request'),
            username=user.get_username(),
            password=attrs['password'],
        )
        if authenticated_user is None:
            raise serializers.ValidationError('Invalid email or password.')

        refresh = RefreshToken.for_user(authenticated_user)
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(authenticated_user).data,
        }


class GoogleLoginSerializer(serializers.Serializer):
    id_token = serializers.CharField(write_only=True, trim_whitespace=True)


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def save(self):
        refresh_token = self.validated_data["refresh"]
        token = RefreshToken(refresh_token)
        token.blacklist()


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def save(self):
        from .services import PasswordResetService

        PasswordResetService.send_reset_email(self.validated_data["email"])


class ResetPasswordSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        from .services import PasswordResetService

        attrs["user"] = PasswordResetService.validate_reset_request(
            uid=attrs["uid"],
            token=attrs["token"],
            password=attrs["password"],
        )
        return attrs

    def save(self):
        from .services import PasswordResetService

        PasswordResetService.reset_password(
            user=self.validated_data["user"],
            password=self.validated_data["password"],
        )
