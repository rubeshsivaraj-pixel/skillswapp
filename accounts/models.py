from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class CustomUser(AbstractUser):
    bio = models.TextField(blank=True, null=True, help_text="Tell others about yourself")
    credits = models.IntegerField(default=3, help_text="Credits earned to spend on learning. You start with 3.")
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True, default='profile_pictures/default.jpg')
    
    # Online status
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(default=timezone.now)
    
    # Verification
    is_verified = models.BooleanField(default=False)
    verification_date = models.DateTimeField(blank=True, null=True)
    
    # Stats
    total_sessions_taught = models.IntegerField(default=0)
    total_sessions_learned = models.IntegerField(default=0)
    average_rating = models.FloatField(default=0.0)

    def __str__(self):
        return self.username

    def mark_online(self):
        self.is_online = True
        self.last_seen = timezone.now()
        self.save()

    def mark_offline(self):
        self.is_online = False
        self.last_seen = timezone.now()
        self.save()
