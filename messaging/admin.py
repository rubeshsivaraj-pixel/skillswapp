from django.contrib import admin
from django.utils.html import format_html
from .models import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'short_content', 'is_read_display', 'timestamp')
    list_filter = ('is_read', 'timestamp')
    search_fields = ('sender__username', 'receiver__username', 'content')
    readonly_fields = ['timestamp']
    ordering = ['-timestamp']
    date_hierarchy = 'timestamp'

    def short_content(self, obj):
        return obj.content[:60] + '…' if len(obj.content) > 60 else obj.content
    short_content.short_description = 'Message'

    def is_read_display(self, obj):
        return format_html('<span style="color:{};">●</span> {}',
                           'green' if obj.is_read else 'gray',
                           'Read' if obj.is_read else 'Unread')
    is_read_display.short_description = 'Read'
    is_read_display.admin_order_field = 'is_read'
