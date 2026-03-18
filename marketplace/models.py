from django.db import models
from accounts.models import CustomUser


class Course(models.Model):
    """A skill or language course available in the marketplace."""
    CATEGORY_CHOICES = [
        ('LANGUAGE', 'Language'),
        ('TECH', 'Technology'),
        ('MUSIC', 'Music'),
        ('ART', 'Art & Design'),
        ('BUSINESS', 'Business'),
        ('SCIENCE', 'Science'),
        ('FITNESS', 'Fitness'),
        ('OTHER', 'Other'),
    ]
    title       = models.CharField(max_length=200)
    description = models.TextField()
    instructor  = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='courses_teaching')
    category    = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='OTHER')
    language    = models.CharField(max_length=5, blank=True, null=True,
                                   help_text='For language courses, the target language code')
    credit_cost = models.IntegerField(default=30, help_text='Credits required to unlock')
    thumbnail   = models.ImageField(upload_to='course_thumbnails/', blank=True, null=True)
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['credit_cost', 'title']

    def __str__(self):
        return f"{self.title} ({self.credit_cost} credits)"


class CoursePurchase(models.Model):
    """Records when a user spends credits to unlock a course."""
    user       = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='course_purchases')
    course     = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='purchases')
    credits_spent = models.IntegerField()
    purchased_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'course')
        ordering = ['-purchased_at']

    def __str__(self):
        return f"{self.user.username} purchased “{self.course.title}”"
