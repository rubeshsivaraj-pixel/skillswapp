"""
Context processors for the SkillSwap application.
Provides global data (notifications, unread counts) to all templates.
"""
from notifications.models import Notification


def notifications_processor(request):
    """
    Add notifications count and recent notifications to template context.
    Only applies to authenticated users.
    """
    if request.user.is_authenticated:
        unread_notifications = request.user.notifications.filter(is_read=False).count()
        recent_notifications = request.user.notifications.filter(is_read=False).order_by('-created_at')[:5]
        return {
            'unread_notifications': unread_notifications,
            'recent_notifications': recent_notifications,
        }
    return {
        'unread_notifications': 0,
        'recent_notifications': [],
    }
