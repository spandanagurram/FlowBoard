from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.common.models import BaseModel


class User(BaseModel, AbstractUser):
    email = models.EmailField(unique=True)
