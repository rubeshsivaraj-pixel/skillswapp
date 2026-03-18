from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .models import FriendRequest, Friendship
from accounts.models import CustomUser
from notifications.models import Notification


@login_required
def friend_list(request):
    friends = Friendship.get_friends(request.user)
    pending_received = FriendRequest.objects.filter(receiver=request.user, status='PENDING')
    pending_sent     = FriendRequest.objects.filter(sender=request.user,   status='PENDING')
    return render(request, 'friends/friend_list.html', {
        'friends': friends,
        'pending_received': pending_received,
        'pending_sent': pending_sent,
    })


@login_required
def send_request(request, username):
    target = get_object_or_404(CustomUser, username=username)
    if target == request.user:
        messages.error(request, "You can't add yourself.")
        return redirect('user_profile', username=username)

    if Friendship.are_friends(request.user, target):
        messages.info(request, f'You are already friends with {target.username}.')
        return redirect('user_profile', username=username)

    freq, created = FriendRequest.objects.get_or_create(
        sender=request.user, receiver=target,
        defaults={'status': 'PENDING'}
    )
    if not created and freq.status == 'REJECTED':
        freq.status = 'PENDING'
        freq.save()
        created = True

    if created:
        Notification.objects.create(
            user=target,
            notification_type='SYSTEM',
            title='New Friend Request',
            message=f'{request.user.username} sent you a friend request.',
        )
        messages.success(request, f'Friend request sent to {target.username}!')
    else:
        messages.info(request, 'Friend request already pending.')
    return redirect('user_profile', username=username)


@login_required
def accept_request(request, request_id):
    freq = get_object_or_404(FriendRequest, pk=request_id, receiver=request.user, status='PENDING')
    freq.status = 'ACCEPTED'
    freq.save()
    u1, u2 = (freq.sender, freq.receiver) if freq.sender.pk < freq.receiver.pk else (freq.receiver, freq.sender)
    Friendship.objects.get_or_create(user1=u1, user2=u2)
    Notification.objects.create(
        user=freq.sender,
        notification_type='SYSTEM',
        title='Friend Request Accepted',
        message=f'{request.user.username} accepted your friend request!',
    )
    messages.success(request, f"You and {freq.sender.username} are now friends!")
    return redirect('friend_list')


@login_required
def reject_request(request, request_id):
    freq = get_object_or_404(FriendRequest, pk=request_id, receiver=request.user, status='PENDING')
    freq.status = 'REJECTED'
    freq.save()
    messages.info(request, 'Request declined.')
    return redirect('friend_list')


@login_required
def unfriend(request, username):
    target = get_object_or_404(CustomUser, username=username)
    u1, u2 = (request.user, target) if request.user.pk < target.pk else (target, request.user)
    Friendship.objects.filter(user1=u1, user2=u2).delete()
    messages.success(request, f'Removed {target.username} from friends.')
    return redirect('friend_list')


@login_required
def friendship_status_api(request, username):
    """Returns JSON with friendship status for profile page buttons."""
    target = get_object_or_404(CustomUser, username=username)
    are_friends = Friendship.are_friends(request.user, target)
    pending = FriendRequest.objects.filter(
        Q(sender=request.user, receiver=target) | Q(sender=target, receiver=request.user),
        status='PENDING'
    ).first()
    return JsonResponse({
        'are_friends': are_friends,
        'pending': bool(pending),
        'pending_sent': bool(pending and pending.sender == request.user),
    })
