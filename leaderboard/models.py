from django.db import models
from accounts.models import CustomUser
from django.db.models import Sum, Count, Avg, Q

class Leaderboard(models.Model):
    """Leaderboard entries for ranking users"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='leaderboard')
    
    # Credits stats
    total_credits_earned = models.IntegerField(default=0)
    total_credits_spent = models.IntegerField(default=0)
    current_credits = models.IntegerField(default=0)
    
    # Session stats
    sessions_taught = models.IntegerField(default=0)
    sessions_learned = models.IntegerField(default=0)
    
    # Rating stats
    average_rating = models.FloatField(default=0.0)
    total_reviews = models.IntegerField(default=0)
    
    # Engagement stats
    skills_offered = models.IntegerField(default=0)
    skills_learned = models.IntegerField(default=0)
    
    # Content stats
    videos_uploaded = models.IntegerField(default=0)
    audio_uploaded = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-total_credits_earned', '-sessions_taught', '-average_rating']
        verbose_name_plural = 'Leaderboards'

    def __str__(self):
        return f"Leaderboard for {self.user.username}"

    @property
    def teacher_rank(self):
        """Get user's rank among teachers"""
        return Leaderboard.objects.filter(
            sessions_taught__gt=self.sessions_taught
        ).count() + 1

    @property
    def learner_rank(self):
        """Get user's rank among learners"""
        return Leaderboard.objects.filter(
            sessions_learned__gt=self.sessions_learned
        ).count() + 1

    @property
    def overall_rank(self):
        """Get user's overall rank based on credits + sessions"""
        score = self.total_credits_earned + (self.sessions_taught * 10)
        return Leaderboard.objects.filter(
            models.Q(total_credits_earned__gt=self.total_credits_earned) |
            (models.Q(total_credits_earned=self.total_credits_earned) & models.Q(sessions_taught__gt=self.sessions_taught))
        ).count() + 1

