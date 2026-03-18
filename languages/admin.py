from django.contrib import admin
from .models import LanguageProfile, LanguageSession, AITutorSession, AITutorMessage, LessonProgress


@admin.register(LanguageProfile)
class LanguageProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'language', 'role', 'proficiency', 'hourly_credits', 'created_at')
    list_filter = ('language', 'role', 'proficiency')
    search_fields = ('user__username',)


@admin.register(LanguageSession)
class LanguageSessionAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'student', 'language', 'credits_paid', 'status', 'created_at')
    list_filter = ('status', 'language')
    search_fields = ('teacher__username', 'student__username')
    list_editable = ('status',)


class AITutorMessageInline(admin.TabularInline):
    model = AITutorMessage
    extra = 0
    readonly_fields = ('role', 'content', 'created_at')
    can_delete = False


@admin.register(AITutorSession)
class AITutorSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'language', 'level', 'credits_spent', 'message_count', 'created_at')
    list_filter  = ('language', 'level')
    search_fields = ('user__username',)
    readonly_fields = ('created_at',)
    inlines = [AITutorMessageInline]


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display  = ('user', 'language', 'proficiency', 'lessons_completed', 'vocab_learned', 'ai_sessions', 'last_studied')
    list_filter   = ('language', 'proficiency')
    search_fields = ('user__username',)
    readonly_fields = ('last_studied',)
