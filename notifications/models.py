from django.db import models
from accounts.models import CustomUser
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('MESSAGE', 'New Message'),
        ('SESSION_REQUEST', 'Session Request'),
        ('SESSION_ACCEPTED', 'Session Accepted'),
        ('SESSION_REJECTED', 'Session Rejected'),
        ('CREDITS_EARNED', 'Credits Earned'),
        ('MATCH_FOUND', 'Match Found'),
        ('REVIEW_RECEIVED', 'Review Received'),
        ('FRIEND_REQUEST', 'Friend Request'),
        ('FRIEND_ACCEPTED', 'Friend Request Accepted'),
        ('SYSTEM', 'System Notification'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Generic FK for linking to any related object (Message, Session, Review, etc.)
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Notifications'

    def __str__(self):
        return f"{self.notification_type} for {self.user.username} - {self.title}"

    def mark_as_read(self):
        self.is_read = True
        self.save()


class SkillMatch(models.Model):
    """Represents a skill match between two users"""
    user1 = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='matches_initiated')
    user2 = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='matches_received')
    
    # Skills being exchanged
    user1_teaches = models.CharField(max_length=100)  # What user1 teaches
    user1_wants = models.CharField(max_length=100)    # What user1 wants to learn
    user2_teaches = models.CharField(max_length=100)  # What user2 teaches
    user2_wants = models.CharField(max_length=100)    # What user2 wants to learn
    
    match_score = models.FloatField(default=0.0, help_text="Score from 0-100 indicating match quality")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user1', 'user2')

    def __str__(self):
        return f"Match between {self.user1.username} and {self.user2.username}"
