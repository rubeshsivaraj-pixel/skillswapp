from django.db import models
from accounts.models import CustomUser

class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    difficulty = models.CharField(
        max_length=20,
        choices=[('BEGINNER', 'Beginner'), ('INTERMEDIATE', 'Intermediate'), ('ADVANCED', 'Advanced')],
        default='BEGINNER'
    )

    def __str__(self):
        return self.name

class UserSkill(models.Model):
    SKILL_TYPES = (
        ('TEACH', 'Can Teach'),
        ('LEARN', 'Want to Learn'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='user_skills')
    skill_type = models.CharField(max_length=10, choices=SKILL_TYPES)
    proficiency = models.CharField(max_length=50, blank=True, null=True, help_text="e.g., Beginner, Intermediate, Expert")

    class Meta:
        unique_together = ('user', 'skill', 'skill_type')

    def __str__(self):
        return f"{self.user.username} - {self.get_skill_type_display()} - {self.skill.name}"


class VideoTutorial(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='videos')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='videos')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    video_file = models.FileField(upload_to='videos/')
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)
    duration = models.IntegerField(blank=True, null=True, help_text="Duration in seconds")
    
    credit_reward = models.IntegerField(default=10, help_text="Credits given when approved")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} by {self.user.username}"


class AudioLesson(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='audio_lessons')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='audio_lessons')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    audio_file = models.FileField(upload_to='audio/')
    duration = models.IntegerField(blank=True, null=True, help_text="Duration in seconds")
    
    credit_reward = models.IntegerField(default=5, help_text="Credits given when approved")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    listens = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Audio Lessons'

    def __str__(self):
        return f"{self.title} by {self.user.username}"


class SkillDemonstration(models.Model):
    """Video demonstrations of skills"""
    STATUS_CHOICES = (
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='demonstrations')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='demonstrations')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    video_file = models.FileField(upload_to='demonstrations/')
    duration = models.IntegerField(blank=True, null=True, help_text="Duration in seconds")
    
    credit_reward = models.IntegerField(default=10)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    views = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} by {self.user.username}"
