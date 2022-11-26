from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    user_type_data = ((1, "Admin"), (2, "Doctor"), (3, "Patient"))
    user_type = models.CharField(default=1, choices=user_type_data, max_length=10)
    birthday = models.DateField()