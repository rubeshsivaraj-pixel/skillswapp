from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse
from .models import Course, CoursePurchase
from credits.views import award_credits
from notifications.models import Notification
from peer_skill_swap.ai_client import build_openai_messages, call_openai_chat


def _build_marketplace_prompt(target_lang):
    return (
        f"You are a knowledgeable, encouraging, and friendly AI tutor on SkillSwap. "
        f"The student wants to practice or learn: {target_lang}. "
        "Support language learning conversations, grammar correction, vocabulary drills, "
        "and skill-learning questions. Keep responses concise and actionable. "
        "When correcting language, format: ❌ wrong -> ✅ correct."
    )


def course_list(request):
    """Public course catalogue."""
    category = request.GET.get('category', '')
    search   = request.GET.get('q', '')
    courses  = Course.objects.filter(is_active=True).select_related('instructor').annotate(
        purchase_count=Count('purchases')
    )
    if category:
        courses = courses.filter(category=category)
    if search:
        courses = courses.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search) |
            Q(instructor__username__icontains=search)
        )

    purchased_ids = []
    if request.user.is_authenticated:
        purchased_ids = list(
            CoursePurchase.objects.filter(user=request.user).values_list('course_id', flat=True)
        )

    CATEGORIES = Course.CATEGORY_CHOICES
    return render(request, 'marketplace/course_list.html', {
        'courses': courses,
        'category': category,
        'search': search,
        'categories': CATEGORIES,
        'purchased_ids': purchased_ids,
    })


@login_required
def purchase_course(request, course_id):
    course = get_object_or_404(Course, pk=course_id, is_active=True)
    if CoursePurchase.objects.filter(user=request.user, course=course).exists():
        messages.info(request, 'You already own this course.')
        return redirect('course_list')
    if request.user.credits < course.credit_cost:
        messages.error(request, f'Not enough credits. Need {course.credit_cost}, have {request.user.credits}.')
        return redirect('course_list')
    success = award_credits(
        user=request.user,
        transaction_type='COURSE_PURCHASE',
        amount=-course.credit_cost,
        description=f'Purchased course: {course.title}',
        related_object_type='Course',
        related_object_id=course.pk,
    )
    if success:
        CoursePurchase.objects.create(user=request.user, course=course, credits_spent=course.credit_cost)
        # Award credits to instructor
        award_credits(
            user=course.instructor,
            transaction_type='TEACH_SESSION',
            amount=max(5, course.credit_cost // 4),
            description=f'Student {request.user.username} purchased your course: {course.title}',
        )
        messages.success(request, f'✅ You unlocked “{course.title}”!')
    else:
        messages.error(request, 'Credit deduction failed.')
    return redirect('purchase_history')


@login_required
def purchase_history(request):
    purchases = CoursePurchase.objects.filter(user=request.user).select_related('course', 'course__instructor')
    return render(request, 'marketplace/purchase_history.html', {'purchases': purchases})


@login_required
def ai_language_chat(request):
    """AI language / skill practice assistant (credits-gated, session-persisted)."""
    AI_COST = 15  # credits per AI message

    # Language choices as (code, name) tuples so the template can iterate correctly
    LANGUAGES = [
        ('English', 'English'), ('Spanish', 'Spanish'), ('French', 'French'),
        ('German', 'German'), ('Italian', 'Italian'), ('Portuguese', 'Portuguese'),
        ('Dutch', 'Dutch'), ('Russian', 'Russian'), ('Arabic', 'Arabic'),
        ('Hindi', 'Hindi'), ('Tamil', 'Tamil'), ('Chinese', 'Chinese'),
        ('Japanese', 'Japanese'), ('Korean', 'Korean'), ('Turkish', 'Turkish'),
        ('Swedish', 'Swedish'), ('Norwegian', 'Norwegian'), ('Greek', 'Greek'),
        ('Polish', 'Polish'), ('Thai', 'Thai'),
    ]

    # Persist chat history in the Django session (keyed per user)
    session_key = f'ai_chat_history_{request.user.pk}'
    history = request.session.get(session_key, [])  # list of {role, content} dicts

    error = None
    selected_language = request.session.get(f'ai_chat_lang_{request.user.pk}', 'Spanish')

    if request.method == 'POST':
        user_message   = request.POST.get('message', '').strip()
        target_lang    = request.POST.get('language', selected_language)
        clear_history  = request.POST.get('clear_chat')

        if clear_history:
            request.session[session_key] = []
            request.session[f'ai_chat_lang_{request.user.pk}'] = target_lang
            return redirect('ai_language_chat')

        if not user_message:
            error = 'Please type a message.'
        elif request.user.credits < AI_COST:
            error = f'Not enough credits. Each message costs {AI_COST} credits. You have {request.user.credits}.'
        else:
            # Deduct credits
            ok = award_credits(
                user=request.user,
                transaction_type='AI_LESSON',
                amount=-AI_COST,
                description=f'AI {target_lang} practice chat',
            )
            if ok:
                # Append user message to history
                history.append({'role': 'user', 'content': user_message})

                # Keep only the last 20 turns to avoid token overflow
                recent_turns = history[-20:]

                # Call OpenAI
                ai_messages = build_openai_messages(_build_marketplace_prompt(target_lang), recent_turns)
                ai_reply, ai_error = call_openai_chat(ai_messages, max_tokens=400, temperature=0.7)
                if ai_error:
                    ai_reply = f"AI is unavailable right now: {ai_error}"

                history.append({'role': 'assistant', 'content': ai_reply})

                # Persist updated history in session
                request.session[session_key] = history
                request.session[f'ai_chat_lang_{request.user.pk}'] = target_lang
                selected_language = target_lang

                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'status': 'ok',
                        'reply': ai_reply,
                        'balance': request.user.credits,
                        'language': target_lang,
                    })
            else:
                error = 'Credit deduction failed. Please try again.'

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and error:
            return JsonResponse({'status': 'error', 'error': error}, status=400)

    return render(request, 'marketplace/ai_chat.html', {
        'history':           history,
        'error':             error,
        'ai_cost':           AI_COST,
        'languages':         LANGUAGES,
        'selected_language': selected_language,
    })


@login_required
def ai_mentor_match(request):
    """AI-powered mentor recommendation."""
    from skills.models import UserSkill
    from accounts.models import CustomUser
    from django.db.models import Avg

    learning_skills = UserSkill.objects.filter(user=request.user, skill_type='LEARN').values_list('skill__name', flat=True)

    mentors = CustomUser.objects.filter(
        skills__skill_type='TEACH',
        skills__skill__name__in=learning_skills,
    ).exclude(id=request.user.id).distinct().annotate(
        avg_rating=Avg('average_rating')
    ).order_by('-avg_rating', '-total_sessions_taught')[:10]

    # Score each mentor
    scored = []
    for m in mentors:
        teaches = list(UserSkill.objects.filter(user=m, skill_type='TEACH').values_list('skill__name', flat=True))
        overlap = set(teaches) & set(learning_skills)
        score = (len(overlap) * 30) + (m.average_rating * 10) + min(m.total_sessions_taught * 2, 30)
        scored.append({'mentor': m, 'score': round(score, 1), 'overlap': list(overlap), 'teaches': teaches})

    scored.sort(key=lambda x: -x['score'])
    return render(request, 'marketplace/ai_mentors.html', {
        'scored_mentors': scored,
        'learning_skills': list(learning_skills),
    })
