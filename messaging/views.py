from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from accounts.models import CustomUser
from .models import Message
from .forms import MessageForm

@login_required
def inbox(request):
    # Get all users the current user has exchanged messages with
    user = request.user
    messages = Message.objects.filter(Q(sender=user) | Q(receiver=user)).order_by('-timestamp')
    
    # Extract unique users from messages
    interacted_users = set()
    for msg in messages:
        if msg.sender != user:
            interacted_users.add(msg.sender)
        if msg.receiver != user:
            interacted_users.add(msg.receiver)
            
    # For a simple chat, we'll just list the users. A real app might show the last message.
    # We can also add users who matched with us, even if no messages yet.
    
    return render(request, 'messaging/inbox.html', {'interacted_users': list(interacted_users)})

@login_required
def chat(request, username):
    other_user = get_object_or_404(CustomUser, username=username)
    
    # Mark messages from other_user to me as read
    Message.objects.filter(sender=other_user, receiver=request.user, is_read=False).update(is_read=True)
    
    # Get conversation history
    messages = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver=other_user)) |
        (Q(sender=other_user) & Q(receiver=request.user))
    ).order_by('timestamp')
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            new_msg = form.save(commit=False)
            new_msg.sender = request.user
            new_msg.receiver = other_user
            new_msg.save()
            return redirect('chat', username=username)
    else:
        form = MessageForm()
        
    context = {
        'other_user': other_user,
        'messages': messages,
        'form': form
    }
    return render(request, 'messaging/chat.html', context)
