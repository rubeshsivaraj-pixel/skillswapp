from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    bio = models.TextField(blank=True, null=True, help_text="Tell others about yourself")
    credits = models.IntegerField(default=3, help_text="Credits earned to spend on learning. You start with 3.")
    
    def __str__(self):
        return self.username
