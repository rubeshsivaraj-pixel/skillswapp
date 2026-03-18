from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Avg, Count, Sum
from skills.models import UserSkill, Skill, VideoTutorial, AudioLesson
from messaging.models import Message
from bookings.models import Session, Review
from notifications.models import Notification, SkillMatch
from leaderboard.models import Leaderboard
from accounts.models import CustomUser
from languages.models import LessonProgress, AITutorSession, LANGUAGE_CHOICES, LESSON_CREDIT_COSTS
from credits.models import CreditTransaction
from marketplace.models import CoursePurchase
from friends.models import Friendship
from friends.models import FriendRequest

def home(request):
    if request.user.is_authenticated:
        return render(request, 'home_authenticated.html')
    return render(request, 'home.html')


@login_required
def video_call(request, username):
    from django.shortcuts import get_object_or_404
    other_user = get_object_or_404(CustomUser, username=username)
    # Sort usernames for a consistent, unique room name
    users = sorted([request.user.username, username])
    room_name = f"skillswap-{users[0]}-{users[1]}"
    jitsi_url = f"https://meet.jit.si/{room_name}"
    return render(request, 'calls/video_call.html', {
        'other_user': other_user,
        'room_name': room_name,
        'jitsi_url': jitsi_url,
        'end_call_url': f"/messages/chat/{other_user.username}/",
    })

@login_required
def dashboard(request):
    user = request.user
    
    # User's skills
    teaching_skills = UserSkill.objects.filter(user=user, skill_type='TEACH').select_related('skill')
    learning_skills = UserSkill.objects.filter(user=user, skill_type='LEARN').select_related('skill')
    
    # Matching algorithm
    wanted_skill_ids = learning_skills.values_list('skill_id', flat=True)
    teaching_skill_ids = teaching_skills.values_list('skill_id', flat=True)
    
    # Find users who teach skills I want to learn
    matches_raw = UserSkill.objects.filter(
        skill_id__in=wanted_skill_ids, 
        skill_type='TEACH'
    ).exclude(user=user).select_related('user', 'skill')
    
    # Group by User
    matched_users = {}
    for match in matches_raw:
        # Bonus: check if they also want to learn what I teach (mutual match)
        is_mutual = UserSkill.objects.filter(
            user=match.user, 
            skill_id__in=teaching_skill_ids, 
            skill_type='LEARN'
        ).exists()
        
        if match.user not in matched_users:
            matched_users[match.user] = {
                'skills': [],
                'is_mutual': is_mutual
            }
        matched_users[match.user]['skills'].append(match.skill)
    
    # Sort: mutual matches first
    sorted_matches = sorted(
        matched_users.items(),
        key=lambda x: (not x[1]['is_mutual'], -x[0].average_rating)
    )
    
    # Recent messages
    recent_messages = Message.objects.filter(
        Q(sender=user) | Q(receiver=user)
    ).order_by('-timestamp').select_related('sender', 'receiver')[:10]
    
    # Unique chat partners
    chat_partners = []
    seen_ids = set()
    for msg in recent_messages:
        other = msg.sender if msg.receiver == user else msg.receiver
        if other.id not in seen_ids:
            seen_ids.add(other.id)
            unread_count = Message.objects.filter(
                sender=other, receiver=user, is_read=False
            ).count()
            chat_partners.append({'user': other, 'last_message': msg, 'unread': unread_count})
    
    # Notifications
    unread_notifications = Notification.objects.filter(user=user, is_read=False).order_by('-created_at')[:5]
    unread_count = unread_notifications.count()
    
    # Credit balance
    credit_balance = user.credits
    
    # Session stats
    upcoming_sessions = Session.objects.filter(
        Q(teacher=user) | Q(student=user),
        status__in=['PENDING', 'ACCEPTED']
    ).order_by('date', 'time')[:5]
    
    # Pending sessions to accept/reject
    pending_sessions = Session.objects.filter(teacher=user, status='PENDING').order_by('date')[:3]
    
    # Uploaded content
    my_videos = VideoTutorial.objects.filter(user=user).order_by('-created_at')[:5]
    my_audio = AudioLesson.objects.filter(user=user).order_by('-created_at')[:5]
    
    # Leaderboard data
    leaderboard = Leaderboard.objects.filter(user=user).first()
    user_rank = None
    if leaderboard:
        user_rank = Leaderboard.objects.filter(
            total_credits_earned__gt=leaderboard.total_credits_earned
        ).count() + 1
    
    # Trending skills (most offered)
    trending_skills = Skill.objects.annotate(
        offer_count=Count('user_skills', filter=Q(user_skills__skill_type='TEACH'))
    ).filter(offer_count__gt=0).order_by('-offer_count')[:8]
    
    # Recommended users (users with good ratings who teach skills I want)
    recommended_mentors = CustomUser.objects.filter(
        skills__skill__in=learning_skills.values('skill'),
        skills__skill_type='TEACH'
    ).exclude(id=user.id).distinct().order_by('-average_rating')[:6]

    # Unified learning history: language + skill progress
    learning_history = []
    for progress in LessonProgress.objects.filter(user=user).order_by('-last_studied'):
        learning_history.append({
            'name': progress.get_language_display(),
            'kind': 'Language',
            'progress_percent': min(100, progress.lessons_completed * 5),
            'lessons_completed': progress.lessons_completed,
            'instructor': 'AI Tutor',
            'last_studied': progress.last_studied,
        })

    for user_skill in learning_skills:
        completed_for_skill = Session.objects.filter(
            student=user,
            skill=user_skill.skill,
            status='COMPLETED',
        ).count()
        learning_history.append({
            'name': user_skill.skill.name,
            'kind': 'Skill',
            'progress_percent': min(100, completed_for_skill * 20),
            'lessons_completed': completed_for_skill,
            'instructor': 'Community Mentors',
            'last_studied': None,
        })

    # Language learning progress
    lang_progress      = LessonProgress.objects.filter(user=user).order_by('-last_studied')[:4]
    active_lang_session = AITutorSession.objects.filter(user=user).order_by('-created_at').first()
    # Recommended languages to try (not yet studied)
    studied_langs = set(lang_progress.values_list('language', flat=True))
    recommended_langs = [
        {'code': code, 'name': name, 'cost': LESSON_CREDIT_COSTS.get(code, 10)}
        for code, name in LANGUAGE_CHOICES
        if code not in studied_langs
    ][:6]
    
    context = {
        'teaching_skills': teaching_skills,
        'learning_skills': learning_skills,
        'matched_users': sorted_matches[:8],
        'chat_partners': chat_partners[:6],
        'unread_notifications': unread_count,
        'recent_notifications': unread_notifications,
        'credit_balance': credit_balance,
        'upcoming_sessions': upcoming_sessions,
        'pending_sessions': pending_sessions,
        'my_videos': my_videos,
        'my_audio': my_audio,
        'leaderboard': leaderboard,
        'user_rank': user_rank,
        'trending_skills': trending_skills,
        'recommended_mentors': recommended_mentors,
        # Language learning
        'lang_progress':        lang_progress,
        'active_lang_session':  active_lang_session,
        'recommended_langs':    recommended_langs,
        'learning_history':     learning_history,
        # ── Popup modal data ───────────────────────────────────────────
        'credit_transactions':  CreditTransaction.objects.filter(user=user).order_by('-created_at')[:30],
        'course_purchases':     CoursePurchase.objects.filter(user=user).select_related('course').order_by('-purchased_at')[:20],
        'lang_progress_all':    LessonProgress.objects.filter(user=user).order_by('-last_studied'),
        'ai_sessions_all':      AITutorSession.objects.filter(user=user).order_by('-created_at')[:20],
        'my_videos_all':        VideoTutorial.objects.filter(user=user).order_by('-created_at')[:20],
        'my_audio_all':         AudioLesson.objects.filter(user=user).order_by('-created_at')[:20],
        'friends_list':         Friendship.get_friends(user)[:20] if hasattr(Friendship, 'get_friends') else [],
        'friend_requests_recent': FriendRequest.objects.filter(
            Q(sender=user) | Q(receiver=user)
        ).select_related('sender', 'receiver').order_by('-updated_at')[:20],
        'language_name_map':    dict(LANGUAGE_CHOICES),
    }
    return render(request, 'dashboard.html', context)
