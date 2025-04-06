from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, blank=True, null=True)  # Username is now optional

    USERNAME_FIELD = 'email'  # Users will log in with email instead of username
    REQUIRED_FIELDS = ['username']  # Django still requires a secondary field

    def __str__(self):
        return self.email


# models.py
class UserProfile(models.Model):
    SUBSCRIPTION_CHOICES = [
        ('free', 'Free'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subscription = models.CharField(max_length=20, choices=SUBSCRIPTION_CHOICES, default='free')
    subscription_expiry = models.DateField(null=True, blank=True)  # Ensure this is present

    def __str__(self):
        return f"{self.user.email} - {self.subscription}"


