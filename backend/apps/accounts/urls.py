from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    ForgotPasswordAPIView,
    GoogleLoginAPIView,
    LoginAPIView,
    LogoutAPIView,
    ProfileAPIView,
    RegisterAPIView,
    ResetPasswordAPIView,
)


urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('forgot-password/', ForgotPasswordAPIView.as_view(), name='forgot_password'),
    path('reset-password/', ResetPasswordAPIView.as_view(), name='reset_password'),
    path('google/', GoogleLoginAPIView.as_view(), name='google_login'),
    path('profile/', ProfileAPIView.as_view(), name='profile'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
]
