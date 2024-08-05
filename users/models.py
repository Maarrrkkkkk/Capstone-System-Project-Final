from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    firstname = models.CharField(max_length=30, blank=False, default='First')
    middle_name = models.CharField(max_length=30, blank=True, null=True)
    lastname = models.CharField(max_length=30, blank=False, default='Last')
    faculty = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ("username",)  # Ensure this is a list or tuple

    def __str__(self):
        return self.username
    

