from django.db import models
from accounts.models import CustomUser

class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

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
