from django.contrib.auth.models import AbstractUser

from apps.common.models import BaseModel


class User(BaseModel, AbstractUser):
    pass
