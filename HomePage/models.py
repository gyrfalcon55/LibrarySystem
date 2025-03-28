from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, blank=True, null=True)  # Username is now optional

    USERNAME_FIELD = 'email'  # Users will log in with email instead of username
    REQUIRED_FIELDS = ['username']  # Django still requires a secondary field

    def __str__(self):
        return self.email
