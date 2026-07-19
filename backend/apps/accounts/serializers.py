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