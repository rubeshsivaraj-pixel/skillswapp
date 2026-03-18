from django.contrib import admin
from .models import Leaderboard

@admin.register(Leaderboard)
class LeaderboardAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_credits_earned', 'sessions_taught', 'average_rating', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__username']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Credits Stats', {'fields': ('total_credits_earned', 'total_credits_spent', 'current_credits')}),
        ('Session Stats', {'fields': ('sessions_taught', 'sessions_learned')}),
        ('Rating Stats', {'fields': ('average_rating', 'total_reviews')}),
        ('Engagement', {'fields': ('skills_offered', 'skills_learned')}),
        ('Content', {'fields': ('videos_uploaded', 'audio_uploaded')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
