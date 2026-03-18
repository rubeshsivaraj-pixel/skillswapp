from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Notification

@login_required
def notification_list(request):
    """Display all notifications for the logged in user"""
    notifications = request.user.notifications.all()[:50]
    
    context = {
        'notifications': notifications,
    }
    return render(request, 'notifications/notification_list.html', context)

@login_required
def mark_notification_read(request, notification_id):
    """Mark a notification as read"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.mark_as_read()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'ok'})
    return redirect('notification_list')

@login_required
def mark_all_read(request):
    """Mark all notifications as read"""
    request.user.notifications.filter(is_read=False).update(is_read=True)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'ok', 'count': 0})
    return redirect('notification_list')

@login_required
def notification_count(request):
    """Return the unread notification count as JSON (for AJAX polling)"""
    count = request.user.notifications.filter(is_read=False).count()
    return JsonResponse({'count': count})
