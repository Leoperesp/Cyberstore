from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    document_number = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=200, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return self.username
