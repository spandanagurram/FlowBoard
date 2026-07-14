from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.common.models import BaseModel


class User(BaseModel, AbstractUser):
    class AuthProvider(models.TextChoices):
        EMAIL = "EMAIL", "Email"
        GOOGLE = "GOOGLE", "Google"

    email = models.EmailField(unique=True)
    auth_provider = models.CharField(
        max_length=20,
        choices=AuthProvider.choices,
        default=AuthProvider.EMAIL,
    )
