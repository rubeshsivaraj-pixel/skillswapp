from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from accounts.models import CustomUser
from .models import Message
from .forms import MessageForm
from notifications.models import Notification
from skills.models import UserSkill

@login_required
def inbox(request):
    """Display inbox with all conversations"""
    user = request.user
    all_messages = Message.objects.filter(Q(sender=user) | Q(receiver=user)).order_by('-timestamp')
    
    # Extract unique conversation partners with last message
    conversation_map = {}
    for msg in all_messages:
        other = msg.sender if msg.receiver == user else msg.receiver
        if other.id not in conversation_map:
            unread_count = Message.objects.filter(sender=other, receiver=user, is_read=False).count()
            conversation_map[other.id] = {
                'user': other,
                'last_message': msg,
                'unread': unread_count,
            }
    
    conversations = sorted(
        conversation_map.values(),
        key=lambda x: x['last_message'].timestamp,
        reverse=True
    )
    
    return render(request, 'messaging/inbox.html', {
        'conversations': conversations,
        'total_unread': sum(c['unread'] for c in conversations),
    })

@login_required
def chat(request, username):
    """Display chat with a specific user"""
    other_user = get_object_or_404(CustomUser, username=username)
    
    # Mark messages from other_user to me as read
    Message.objects.filter(sender=other_user, receiver=request.user, is_read=False).update(is_read=True)
    
    # Get conversation history
    chat_messages = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver=other_user)) |
        (Q(sender=other_user) & Q(receiver=request.user))
    ).order_by('timestamp')
    
    first_teach_skill = UserSkill.objects.filter(user=other_user, skill_type='TEACH').select_related('skill').first()

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            new_msg = form.save(commit=False)
            new_msg.sender = request.user
            new_msg.receiver = other_user
            new_msg.save()
            
            # Create notification for the receiver
            Notification.objects.create(
                user=other_user, 
                notification_type='MESSAGE',
                title=f'New message from {request.user.username}',
                message=new_msg.content[:100]
            )
            
            # For AJAX requests, return the message as JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'ok',
                    'message': {
                        'content': new_msg.content,
                        'sender': new_msg.sender.username,
                        'timestamp': new_msg.timestamp.isoformat(),
                    }
                })
            
            return redirect('chat', username=username)
    else:
        form = MessageForm()
    
    # Build conversations list for sidebar
    all_msgs = Message.objects.filter(Q(sender=request.user) | Q(receiver=request.user)).order_by('-timestamp')
    conv_map = {}
    for msg in all_msgs:
        other = msg.sender if msg.receiver == request.user else msg.receiver
        if other.id not in conv_map:
            conv_map[other.id] = {
                'user': other,
                'last_message': msg,
                'unread': Message.objects.filter(sender=other, receiver=request.user, is_read=False).count(),
            }
    conversations = sorted(conv_map.values(), key=lambda x: x['last_message'].timestamp, reverse=True)

    return render(request, 'messaging/chat.html', {
        'other_user': other_user,
        'chat_messages': chat_messages,
        'form': form,
        'conversations': conversations,
        'first_teach_skill': first_teach_skill,
    })

@login_required
def send_message_api(request, username):
    """API endpoint for sending messages"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    other_user = get_object_or_404(CustomUser, username=username)
    content = request.POST.get('content', '').strip()
    
    if not content:
        return JsonResponse({'error': 'Message cannot be empty'}, status=400)
    
    message = Message.objects.create(
        sender=request.user,
        receiver=other_user,
        content=content
    )
    
    # Create notification for the receiver
    Notification.objects.create(
        user=other_user,
        notification_type='MESSAGE',
        title=f'New message from {request.user.username}',
        message=content[:100]
    )
    
    return JsonResponse({
        'status': 'ok',
        'message': {
            'id': message.id,
            'content': message.content,
            'sender': message.sender.username,
            'timestamp': message.timestamp.isoformat(),
        }
    })
