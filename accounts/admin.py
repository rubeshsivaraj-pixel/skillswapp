from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'credits_badge', 'is_online_display', 'average_rating', 'is_verified', 'is_staff', 'date_joined']
    list_filter = ['is_staff', 'is_superuser', 'is_online', 'is_verified', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    readonly_fields = ['date_joined', 'last_login', 'last_seen', 'average_rating',
                       'total_sessions_taught', 'total_sessions_learned']
    actions = ['mark_verified', 'mark_unverified', 'set_online', 'set_offline']

    fieldsets = UserAdmin.fieldsets + (
        ('Profile', {
            'fields': ('bio', 'profile_picture', 'is_verified', 'verification_date')
        }),
        ('Credits & Status', {
            'fields': ('credits', 'is_online', 'last_seen')
        }),
        ('Stats', {
            'fields': ('average_rating', 'total_sessions_taught', 'total_sessions_learned')
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('bio', 'credits')}),
    )

    def credits_badge(self, obj):
        colour = 'green' if obj.credits >= 20 else 'orange' if obj.credits >= 5 else 'red'
        return format_html('<span style="color:{};font-weight:bold;">{}</span>', colour, obj.credits)
    credits_badge.short_description = 'Credits'
    credits_badge.admin_order_field = 'credits'

    def is_online_display(self, obj):
        dot = '🟢' if obj.is_online else '⚫'
        return format_html('{}', dot)
    is_online_display.short_description = 'Online'
    is_online_display.admin_order_field = 'is_online'

    @admin.action(description='Mark selected users as verified')
    def mark_verified(self, request, queryset):
        from django.utils import timezone
        queryset.update(is_verified=True, verification_date=timezone.now())

    @admin.action(description='Mark selected users as unverified')
    def mark_unverified(self, request, queryset):
        queryset.update(is_verified=False, verification_date=None)

    @admin.action(description='Set selected users online')
    def set_online(self, request, queryset):
        queryset.update(is_online=True)

    @admin.action(description='Set selected users offline')
    def set_offline(self, request, queryset):
        queryset.update(is_online=False)
