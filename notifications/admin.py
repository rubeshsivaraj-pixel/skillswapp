from django.contrib import admin
from .models import Notification, SkillMatch


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'notification_type', 'title', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    list_editable = ['is_read']
    search_fields = ['user__username', 'title', 'message']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    actions = ['mark_all_read', 'mark_all_unread']

    fieldsets = (
        ('User & Type', {'fields': ('user', 'notification_type')}),
        ('Content', {'fields': ('title', 'message')}),
        ('Related Object', {'fields': ('content_type', 'object_id')}),
        ('Status', {'fields': ('is_read', 'created_at', 'updated_at')}),
    )

    @admin.action(description='Mark selected notifications as read')
    def mark_all_read(self, request, queryset):
        queryset.update(is_read=True)

    @admin.action(description='Mark selected notifications as unread')
    def mark_all_unread(self, request, queryset):
        queryset.update(is_read=False)


@admin.register(SkillMatch)
class SkillMatchAdmin(admin.ModelAdmin):
    list_display = ['user1', 'user2', 'match_score', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['user1__username', 'user2__username']
    readonly_fields = ['created_at']
    ordering = ['-match_score']
