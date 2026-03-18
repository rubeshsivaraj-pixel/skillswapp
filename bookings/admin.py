from django.contrib import admin
from django.utils.html import format_html
from .models import Session, Review


class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    readonly_fields = ['created_at']
    fields = ['reviewer', 'reviewee', 'rating', 'comment', 'created_at']


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('skill', 'teacher', 'student', 'date', 'time', 'status_badge', 'created_at')
    list_filter = ('status', 'date', 'created_at')
    search_fields = ('teacher__username', 'student__username', 'skill__name')
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-date', '-time']
    date_hierarchy = 'date'
    inlines = [ReviewInline]
    actions = ['mark_completed', 'mark_cancelled']

    fieldsets = (
        ('Participants', {'fields': ('teacher', 'student', 'skill')}),
        ('Schedule', {'fields': ('date', 'time')}),
        ('Status', {'fields': ('status',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

    def status_badge(self, obj):
        colours = {
            'PENDING':   ('#856404', '#fff3cd'),
            'CONFIRMED': ('#0f5132', '#d1e7dd'),
            'COMPLETED': ('#084298', '#cfe2ff'),
            'CANCELLED': ('#842029', '#f8d7da'),
        }
        fg, bg = colours.get(obj.status, ('#333', '#eee'))
        return format_html(
            '<span style="background:{};color:{};padding:2px 8px;border-radius:4px;font-size:0.85em;">{}</span>',
            bg, fg, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'

    @admin.action(description='Mark selected sessions as Completed')
    def mark_completed(self, request, queryset):
        queryset.update(status='COMPLETED')

    @admin.action(description='Mark selected sessions as Cancelled')
    def mark_cancelled(self, request, queryset):
        queryset.update(status='CANCELLED')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('session', 'reviewer', 'reviewee', 'star_rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('reviewer__username', 'reviewee__username')
    readonly_fields = ['created_at']
    ordering = ['-created_at']

    fieldsets = (
        ('Review Details', {'fields': ('session', 'reviewer', 'reviewee')}),
        ('Rating', {'fields': ('rating', 'comment')}),
        ('Timestamp', {'fields': ('created_at',)}),
    )

    def star_rating(self, obj):
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return format_html('<span style="color:#f59e0b;font-size:1.1em;">{}</span>', stars)
    star_rating.short_description = 'Rating'
    star_rating.admin_order_field = 'rating'
