from django.db import models
from accounts.models import CustomUser

class CreditTransaction(models.Model):
    TRANSACTION_TYPES = (
        ('UPLOAD_VIDEO', 'Upload Tutorial Video'),
        ('UPLOAD_AUDIO', 'Upload Audio Lesson'),
        ('TEACH_SESSION', 'Teach Skill Session'),
        ('HELP_LEARNER', 'Help Another Learner'),
        ('BOOK_SESSION', 'Book Learning Session'),
        ('COURSE_PURCHASE', 'Purchase Course'),
        ('LANG_SESSION', 'Language Session'),
        ('AI_LESSON', 'AI Language Lesson'),
        ('REFERRAL', 'Referral Bonus'),
        ('ADMIN_AWARD', 'Admin Award'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='credit_transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.IntegerField()
    description = models.TextField(blank=True, null=True)
    
    # Reference to related object (Video, Audio, Session, etc.)
    related_object_type = models.CharField(max_length=50, blank=True, null=True)
    related_object_id = models.IntegerField(blank=True, null=True)
    
    balance_after = models.IntegerField()  # Balance after transaction
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        action = "earned" if self.amount > 0 else "spent"
        return f"{self.user.username} {action} {abs(self.amount)} credits ({self.get_transaction_type_display()})"


class CreditPackage(models.Model):
    """Pre-defined credit packages for purchasing"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    credits = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # In USD or other currency
    bonus_credits = models.IntegerField(default=0)  # Bonus credits if purchased
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['credits']

    def __str__(self):
        return f"{self.name} - {self.credits} credits for ${self.price}"

    @property
    def total_credits(self):
        return self.credits + self.bonus_credits

