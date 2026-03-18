from django.contrib import admin
from django.utils import timezone
from .models import Skill, UserSkill, VideoTutorial, AudioLesson, SkillDemonstration


def _approve(modeladmin, request, queryset):
    queryset.update(status='APPROVED', approved_at=timezone.now())
    # Trigger per-instance save so signals fire
    for obj in queryset:
        obj.save(update_fields=['status', 'approved_at'])
_approve.short_description = 'Approve selected (award credits)'


def _reject(modeladmin, request, queryset):
    queryset.update(status='REJECTED')
_reject.short_description = 'Reject selected'

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'difficulty')
    list_filter = ('category', 'difficulty')
    search_fields = ('name', 'description')

@admin.register(UserSkill)
class UserSkillAdmin(admin.ModelAdmin):
    list_display = ('user', 'skill', 'skill_type', 'proficiency')
    list_filter = ('skill_type', 'skill')
    search_fields = ('user__username', 'skill__name')

@admin.register(VideoTutorial)
class VideoTutorialAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'skill', 'status', 'views', 'created_at')
    list_filter = ('status', 'skill', 'created_at')
    list_editable = ('status',)
    search_fields = ('title', 'user__username', 'skill__name')
    readonly_fields = ['created_at', 'updated_at', 'views', 'likes']
    actions = [_approve, _reject]

    fieldsets = (
        ('Basic Info', {'fields': ('title', 'description', 'user', 'skill')}),
        ('Files', {'fields': ('video_file', 'thumbnail', 'duration')}),
        ('Engagement', {'fields': ('views', 'likes')}),
        ('Credits & Status', {'fields': ('credit_reward', 'status', 'approved_at')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

@admin.register(AudioLesson)
class AudioLessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'skill', 'status', 'listens', 'created_at')
    list_filter = ('status', 'skill', 'created_at')
    list_editable = ('status',)
    search_fields = ('title', 'user__username', 'skill__name')
    readonly_fields = ['created_at', 'updated_at', 'listens', 'likes']
    actions = [_approve, _reject]

    fieldsets = (
        ('Basic Info', {'fields': ('title', 'description', 'user', 'skill')}),
        ('Files', {'fields': ('audio_file', 'duration')}),
        ('Engagement', {'fields': ('listens', 'likes')}),
        ('Credits & Status', {'fields': ('credit_reward', 'status', 'approved_at')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

@admin.register(SkillDemonstration)
class SkillDemonstrationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'skill', 'status', 'views', 'created_at')
    list_filter = ('status', 'skill', 'created_at')
    search_fields = ('title', 'user__username', 'skill__name')
    readonly_fields = ['created_at', 'updated_at', 'views']
    
    fieldsets = (
        ('Basic Info', {'fields': ('title', 'description', 'user', 'skill')}),
        ('Files', {'fields': ('video_file', 'duration')}),
        ('Engagement', {'fields': ('views',)}),
        ('Credits & Status', {'fields': ('credit_reward', 'status')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
