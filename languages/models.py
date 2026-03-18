from django.db import models
from accounts.models import CustomUser

LANGUAGE_CHOICES = [
    ('en', 'English'), ('es', 'Spanish'), ('fr', 'French'), ('de', 'German'),
    ('it', 'Italian'), ('pt', 'Portuguese'), ('nl', 'Dutch'), ('ru', 'Russian'),
    ('ar', 'Arabic'), ('hi', 'Hindi'), ('ta', 'Tamil'), ('zh', 'Chinese'),
    ('ja', 'Japanese'), ('ko', 'Korean'), ('tr', 'Turkish'), ('sv', 'Swedish'),
    ('no', 'Norwegian'), ('el', 'Greek'), ('pl', 'Polish'), ('th', 'Thai'),
    ('vi', 'Vietnamese'), ('id', 'Indonesian'), ('ms', 'Malay'), ('uk', 'Ukrainian'),
]

# Credit cost per AI lesson start (deducted once per session)
LESSON_CREDIT_COSTS = {
    'en': 10, 'es': 10, 'fr': 10, 'de': 10,
    'it': 10, 'pt': 10, 'nl': 10, 'ru': 10,
    'ar': 10, 'hi': 10, 'ta': 10, 'zh': 12,
    'ja': 12, 'ko': 10, 'tr': 10, 'sv': 10,
    'no': 10, 'el': 10, 'pl': 10, 'th': 10,
    'vi': 10, 'id': 10, 'ms': 10, 'uk': 10,
}

LESSON_LEVELS = [
    ('beginner', 'Beginner'),
    ('intermediate', 'Intermediate'),
    ('advanced', 'Advanced'),
    ('conversation', 'Conversation Practice'),
    ('vocabulary', 'Vocabulary Training'),
]


class LanguageProfile(models.Model):
    """A user offering or wanting to learn a language."""
    ROLE_CHOICES = [('TEACH', 'Teach'), ('LEARN', 'Learn')]
    user     = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='language_profiles')
    language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES)
    role     = models.CharField(max_length=5, choices=ROLE_CHOICES)
    proficiency = models.CharField(
        max_length=20,
        choices=[('Beginner', 'Beginner'), ('Intermediate', 'Intermediate'), ('Advanced', 'Advanced'), ('Native', 'Native')],
        default='Intermediate'
    )
    hourly_credits = models.IntegerField(default=20, help_text='Credits per 1-hour session')
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'language', 'role')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} — {self.get_role_display()} {self.get_language_display()}"


class LanguageSession(models.Model):
    """Booked language learning session."""
    STATUS = [('PENDING','Pending'),('CONFIRMED','Confirmed'),('COMPLETED','Completed'),('CANCELLED','Cancelled')]
    teacher  = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='lang_sessions_teaching')
    student  = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='lang_sessions_learning')
    language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES)
    credits_paid = models.IntegerField(default=20)
    status   = models.CharField(max_length=10, choices=STATUS, default='PENDING')
    scheduled_at = models.DateTimeField(null=True, blank=True)
    notes    = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student} learns {self.get_language_display()} from {self.teacher}"


# ── AI Language Tutor ─────────────────────────────────────────────────────────

class AITutorSession(models.Model):
    """One paid AI tutoring session for a user."""
    user          = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='ai_tutor_sessions')
    language      = models.CharField(max_length=5, choices=LANGUAGE_CHOICES)
    level         = models.CharField(max_length=20, choices=LESSON_LEVELS, default='beginner')
    credits_spent = models.IntegerField(default=10)
    message_count = models.IntegerField(default=0)
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} — AI {self.get_language_display()} ({self.level})"


class AITutorMessage(models.Model):
    """A single message turn in an AI tutor session."""
    ROLE_CHOICES = [('user', 'User'), ('assistant', 'AI Tutor')]
    session    = models.ForeignKey(AITutorSession, on_delete=models.CASCADE, related_name='messages')
    role       = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"[{self.role}] {self.content[:60]}"


class LessonProgress(models.Model):
    """Tracks a user's overall progress for a specific language."""
    PROFICIENCY_LEVELS = [
        ('Beginner',     'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced',     'Advanced'),
    ]
    user              = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='lesson_progress')
    language          = models.CharField(max_length=5, choices=LANGUAGE_CHOICES)
    lessons_completed = models.IntegerField(default=0)
    vocab_learned     = models.IntegerField(default=0)
    ai_sessions       = models.IntegerField(default=0)
    proficiency       = models.CharField(max_length=20, choices=PROFICIENCY_LEVELS, default='Beginner')
    last_studied      = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'language')
        ordering = ['-last_studied']

    def __str__(self):
        return f"{self.user.username} — {self.get_language_display()} ({self.proficiency})"
