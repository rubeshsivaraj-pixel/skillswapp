from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Count
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser
from skills.models import UserSkill, VideoTutorial
from bookings.models import Review, Session
from leaderboard.models import Leaderboard
from notifications.models import SkillMatch
from friends.models import Friendship, FriendRequest

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            # Create leaderboard entry for new user
            Leaderboard.objects.get_or_create(user=user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def profile(request, username=None):
    if username:
        profile_user = get_object_or_404(CustomUser, username=username)
    else:
        profile_user = request.user

    is_owner = (request.user == profile_user)
    
    # Friend status (for non-owner viewing another user's profile)
    are_friends = False
    pending_request = None
    pending_sent = False
    if not is_owner and request.user.is_authenticated:
        are_friends = Friendship.are_friends(request.user, profile_user)
        if not are_friends:
            pending_request = FriendRequest.objects.filter(
                sender=profile_user, receiver=request.user, status='PENDING'
            ).first()
            pending_sent = FriendRequest.objects.filter(
                sender=request.user, receiver=profile_user, status='PENDING'
            ).exists()
    
    # Get user's skills
    teaching_skills = profile_user.skills.filter(skill_type='TEACH')
    learning_skills = profile_user.skills.filter(skill_type='LEARN')
    
    # Get user's average rating
    reviews = Review.objects.filter(reviewee=profile_user)
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    # Get user's leaderboard rank
    leaderboard = Leaderboard.objects.filter(user=profile_user).first()
    
    context = {
        'profile_user': profile_user,
        'is_owner': is_owner,
        'teaching_skills': teaching_skills,
        'learning_skills': learning_skills,
        'avg_rating': round(avg_rating, 1) if avg_rating else 0,
        'total_reviews': reviews.count(),
        'reviews': reviews.select_related('reviewer').order_by('-created_at')[:10],
        'leaderboard': leaderboard,
        'unread_notifications': request.user.notifications.filter(is_read=False).count() if is_owner else 0,
        'are_friends': are_friends,
        'pending_request': pending_request,
        'pending_sent': pending_sent,
        'profile_videos': VideoTutorial.objects.filter(user=profile_user, status='APPROVED').order_by('-created_at')[:6],
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = CustomUserChangeForm(instance=request.user)
    return render(request, 'accounts/edit_profile.html', {'form': form})

@login_required
def discover_users(request):
    """Display all users except the logged-in user"""
    # Get all users except current user
    users = CustomUser.objects.exclude(id=request.user.id).select_related().prefetch_related('skills')
    
    # Filter by search query
    search_query = request.GET.get('search', '')
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(bio__icontains=search_query) |
            Q(skills__skill__name__icontains=search_query)
        ).distinct()
    
    # Filter by skill
    skill_filter = request.GET.get('skill', '')
    if skill_filter:
        users = users.filter(
            Q(skills__skill__name__icontains=skill_filter)
        ).distinct()
    
    # Sort by rating
    sort_by = request.GET.get('sort', '-average_rating')
    if sort_by == 'newest':
        users = users.order_by('-date_joined')
    elif sort_by == 'most_active':
        users = users.annotate(sessions=Count('teaching_sessions')).order_by('-sessions')
    else:
        users = users.order_by('-average_rating')
    
    # Pagination
    paginator = Paginator(users, 12)
    page_number = request.GET.get('page', 1)
    users_page = paginator.get_page(page_number)
    
    # Get user's matches
    user_matches = SkillMatch.objects.filter(
        Q(user1=request.user) | Q(user2=request.user),
        is_active=True
    ).values_list('user1_id', 'user2_id')
    
    matched_user_ids = set()
    for match in user_matches:
        matched_user_ids.add(match[0])
        matched_user_ids.add(match[1])
    
    context = {
        'users_page': users_page,
        'search_query': search_query,
        'skill_filter': skill_filter,
        'sort_by': sort_by,
        'matched_user_ids': matched_user_ids,
    }
    return render(request, 'accounts/discover.html', context)

@login_required
def leaderboard(request):
    """Display leaderboard rankings"""
    leaderboard_entries = Leaderboard.objects.all().select_related('user')
    
    # Get different rankings
    top_teachers = leaderboard_entries.order_by('-sessions_taught')[:10]
    top_learners = leaderboard_entries.order_by('-sessions_learned')[:10]
    top_rated = leaderboard_entries.order_by('-average_rating')[:10]
    top_contributors = leaderboard_entries.order_by('-total_credits_earned')[:10]
    
    # Get current user's rank
    user_leaderboard = leaderboard_entries.filter(user=request.user).first()
    user_rank = None
    if user_leaderboard:
        user_rank = leaderboard_entries.filter(
            total_credits_earned__gt=user_leaderboard.total_credits_earned
        ).count() + 1
    
    context = {
        'top_teachers': top_teachers,
        'top_learners': top_learners,
        'top_rated': top_rated,
        'top_contributors': top_contributors,
        'user_rank': user_rank,
        'user_leaderboard': user_leaderboard,
    }
    return render(request, 'accounts/leaderboard.html', context)
