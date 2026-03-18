from django.db import models
from accounts.models import CustomUser


class FriendRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
    ]
    sender   = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_requests')
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_requests')
    status   = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('sender', 'receiver')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.sender} → {self.receiver} [{self.status}]"


class Friendship(models.Model):
    """Bidirectional friendship record — created when request is accepted."""
    user1 = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='friendships1')
    user2 = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='friendships2')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user1', 'user2')

    def __str__(self):
        return f"{self.user1.username} ↔ {self.user2.username}"

    @classmethod
    def are_friends(cls, user_a, user_b):
        u1, u2 = (user_a, user_b) if user_a.pk < user_b.pk else (user_b, user_a)
        return cls.objects.filter(user1=u1, user2=u2).exists()

    @classmethod
    def get_friends(cls, user):
        ids = list(
            cls.objects.filter(user1=user).values_list('user2_id', flat=True)
        ) + list(
            cls.objects.filter(user2=user).values_list('user1_id', flat=True)
        )
        return CustomUser.objects.filter(pk__in=ids)
