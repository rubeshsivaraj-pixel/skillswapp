from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import Http404
from django.http import JsonResponse

from .models import (
    LanguageProfile, LanguageSession, AITutorSession, AITutorMessage,
    LessonProgress, LANGUAGE_CHOICES, LESSON_CREDIT_COSTS, LESSON_LEVELS,
)
from credits.views import award_credits
from notifications.models import Notification
from peer_skill_swap.ai_client import build_openai_messages, call_openai_chat


# ── Shared helpers ────────────────────────────────────────────────────────────

def _build_system_prompt(lang_name, level):
    focus = {
        'beginner':     (
            'Focus on basic vocabulary, simple greetings, numbers, colors, and common phrases. '
            'Use very simple language and explain everything clearly in English too.'
        ),
        'intermediate': (
            'Focus on grammar rules, broader vocabulary, everyday conversation topics, '
            'and gently correct any mistakes the student makes.'
        ),
        'advanced':     (
            'Focus on fluency, complex grammar structures, idioms, nuanced vocabulary, '
            'and have sophisticated discussions primarily in the target language.'
        ),
        'conversation': (
            'Have a natural, flowing conversation. Silently note grammar mistakes and at the end '
            'of each response provide a short "Corrections & Tips" section.'
        ),
        'vocabulary':   (
            'Each response should introduce 5–8 new vocabulary words with pronunciation hints, '
            'an example sentence, and a memory tip. Then quiz the student on previous words.'
        ),
    }.get(level, 'Provide comprehensive, beginner-friendly language instruction.')
    return (
        f"You are an expert, friendly, and encouraging {lang_name} language tutor. "
        f"The student is at the {level} level. {focus} "
        f"Always be patient. Format error corrections clearly: "
        f"❌ Wrong form → ✅ Correct form. "
        f"Respond primarily in {lang_name} with English explanations where it aids learning."
    )


# ── Language Marketplace (human tutors) ──────────────────────────────────────

def language_marketplace(request):
    """Browse all language teachers globally."""
    lang_filter = request.GET.get('lang', '')
    search      = request.GET.get('q', '')
    teachers    = LanguageProfile.objects.filter(role='TEACH').select_related('user')
    if lang_filter:
        teachers = teachers.filter(language=lang_filter)
    if search:
        teachers = teachers.filter(
            Q(user__username__icontains=search) |
            Q(user__first_name__icontains=search) |
            Q(bio__icontains=search)
        )
    return render(request, 'languages/marketplace.html', {
        'teachers': teachers,
        'language_choices': LANGUAGE_CHOICES,
        'lang_filter': lang_filter,
        'search': search,
    })


@login_required
def my_languages(request):
    profiles = LanguageProfile.objects.filter(user=request.user)
    return render(request, 'languages/my_languages.html', {
        'profiles': profiles,
        'language_choices': LANGUAGE_CHOICES,
    })


@login_required
def add_language(request):
    if request.method == 'POST':
        language   = request.POST.get('language')
        role       = request.POST.get('role')
        proficiency = request.POST.get('proficiency', 'Intermediate')
        credits    = int(request.POST.get('hourly_credits', 20))
        bio        = request.POST.get('bio', '')
        if not language or not role:
            messages.error(request, 'Language and role are required.')
        else:
            LanguageProfile.objects.update_or_create(
                user=request.user, language=language, role=role,
                defaults={'proficiency': proficiency, 'hourly_credits': credits, 'bio': bio},
            )
            messages.success(request, 'Language profile saved!')
            return redirect('my_languages')
    return render(request, 'languages/add_language.html', {'language_choices': LANGUAGE_CHOICES})


@login_required
def book_language_session(request, teacher_id):
    teacher_profile = get_object_or_404(LanguageProfile, pk=teacher_id, role='TEACH')
    if request.method == 'POST':
        cost = teacher_profile.hourly_credits
        if request.user.credits < cost:
            messages.error(request, f'Not enough credits. You need {cost}, you have {request.user.credits}.')
            return redirect('language_marketplace')
        success = award_credits(
            user=request.user,
            transaction_type='LANG_SESSION',
            amount=-cost,
            description=f'Language session: learn {teacher_profile.get_language_display()} from {teacher_profile.user.username}',
        )
        if success:
            LanguageSession.objects.create(
                teacher=teacher_profile.user,
                student=request.user,
                language=teacher_profile.language,
                credits_paid=cost,
                scheduled_at=request.POST.get('scheduled_at') or None,
                notes=request.POST.get('notes', '').strip(),
            )
            Notification.objects.create(
                user=teacher_profile.user,
                notification_type='SESSION_REQUEST',
                title='New language session booked',
                message=f'{request.user.username} booked a {teacher_profile.get_language_display()} session with you.',
            )
            messages.success(request, f'Session booked! {cost} credits deducted.')
            return redirect('my_lang_sessions')
    return render(request, 'languages/book_session.html', {
        'teacher': teacher_profile.user,
        'teacher_profile': teacher_profile,
    })


@login_required
def my_lang_sessions(request):
    teaching = LanguageSession.objects.filter(teacher=request.user)
    learning = LanguageSession.objects.filter(student=request.user)
    return render(request, 'languages/my_sessions.html', {
        'teaching': teaching,
        'learning': learning,
    })


# ── AI Language Tutor ─────────────────────────────────────────────────────────

def ai_tutor_home(request):
    """Public-facing AI tutor landing page with language cards."""
    progress_map = {}
    if request.user.is_authenticated:
        for p in LessonProgress.objects.filter(user=request.user):
            progress_map[p.language] = p

    languages_data = [
        {
            'code':     code,
            'name':     name,
            'cost':     LESSON_CREDIT_COSTS.get(code, 10),
            'progress': progress_map.get(code),
        }
        for code, name in LANGUAGE_CHOICES
    ]
    return render(request, 'languages/ai_tutor.html', {'languages_data': languages_data})


@login_required
def lesson_modules(request, lang_code):
    """Module selection page for a specific language."""
    lang_name = dict(LANGUAGE_CHOICES).get(lang_code)
    if not lang_name:
        raise Http404('Language not found')
    cost            = LESSON_CREDIT_COSTS.get(lang_code, 10)
    progress        = LessonProgress.objects.filter(user=request.user, language=lang_code).first()
    recent_sessions = AITutorSession.objects.filter(user=request.user, language=lang_code)[:5]
    return render(request, 'languages/lesson_modules.html', {
        'lang_code':       lang_code,
        'lang_name':       lang_name,
        'cost':            cost,
        'progress':        progress,
        'levels':          LESSON_LEVELS,
        'recent_sessions': recent_sessions,
    })


@login_required
def start_ai_session(request, lang_code):
    """Deduct credits and open a new AI tutor session."""
    if request.method != 'POST':
        return redirect('lesson_modules', lang_code=lang_code)

    lang_name = dict(LANGUAGE_CHOICES).get(lang_code)
    if not lang_name:
        raise Http404('Language not found')

    level = request.POST.get('level', 'beginner')
    if level not in dict(LESSON_LEVELS):
        level = 'beginner'

    cost = LESSON_CREDIT_COSTS.get(lang_code, 10)
    if request.user.credits < cost:
        messages.error(request, f'Not enough credits. This lesson costs {cost} credits but you only have {request.user.credits}.')
        return redirect('lesson_modules', lang_code=lang_code)

    success = award_credits(
        user=request.user,
        transaction_type='AI_LESSON',
        amount=-cost,
        description=f'AI {lang_name} lesson — {dict(LESSON_LEVELS).get(level, level.title())}',
    )
    if not success:
        messages.error(request, 'Credit deduction failed. Please try again.')
        return redirect('lesson_modules', lang_code=lang_code)

    session = AITutorSession.objects.create(
        user=request.user,
        language=lang_code,
        level=level,
        credits_spent=cost,
    )

    # Update or create progress record
    progress, _ = LessonProgress.objects.get_or_create(
        user=request.user,
        language=lang_code,
        defaults={'proficiency': 'Beginner'},
    )
    progress.ai_sessions += 1
    progress.save()

    # Generate initial AI greeting / lesson opener
    system_prompt = _build_system_prompt(lang_name, level)
    greeting, _ = call_openai_chat(build_openai_messages(system_prompt, [
        {'role': 'user', 'content': f'Hello! I want to start my {level}-level {lang_name} lesson. Please greet me and begin.'},
    ]), max_tokens=450, temperature=0.7)
    AITutorMessage.objects.create(
        session=session,
        role='assistant',
        content=greeting or f"Hello! I'm your {lang_name} AI tutor. Let's begin your {level} lesson. What would you like to practice first?",
    )

    messages.success(request, f'{cost} credits deducted. Your {lang_name} lesson has started!')
    return redirect('ai_lesson_chat', session_id=session.id)


@login_required
def ai_lesson_chat(request, session_id):
    """Chat view for an active AI tutor session."""
    session  = get_object_or_404(AITutorSession, pk=session_id, user=request.user)
    lang_name = dict(LANGUAGE_CHOICES).get(session.language, session.language)

    if request.method == 'POST':
        user_text = request.POST.get('message', '').strip()
        if user_text:
            AITutorMessage.objects.create(session=session, role='user', content=user_text)
            session.message_count += 1
            session.save()

            # Build context: system prompt + last 20 messages (10 turns)
            system_prompt = _build_system_prompt(lang_name, session.level)
            history = []
            for m in session.messages.order_by('created_at'):
                history.append({'role': m.role if m.role == 'user' else 'assistant', 'content': m.content})

            ai_reply, ai_error = call_openai_chat(
                build_openai_messages(system_prompt, history[-20:]),
                max_tokens=450,
                temperature=0.7,
            )
            if not ai_reply:
                ai_reply = f"I couldn't respond right now. {ai_error or 'Please try again in a moment.'}"
            AITutorMessage.objects.create(session=session, role='assistant', content=ai_reply)

            # Every 5 user messages counts as one completed lesson milestone
            if session.message_count > 0 and session.message_count % 5 == 0:
                progress, _ = LessonProgress.objects.get_or_create(
                    user=request.user,
                    language=session.language,
                    defaults={'proficiency': 'Beginner'},
                )
                progress.lessons_completed += 1
                progress.vocab_learned     += 4   # ~4 vocab items per 5 exchanges
                if progress.lessons_completed >= 20:
                    progress.proficiency = 'Advanced'
                elif progress.lessons_completed >= 8:
                    progress.proficiency = 'Intermediate'
                progress.save()

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'ok',
                    'reply': ai_reply,
                    'message_count': session.message_count,
                })

        return redirect('ai_lesson_chat', session_id=session.id)

    chat_messages = session.messages.order_by('created_at')
    return render(request, 'languages/ai_lesson_chat.html', {
        'session':       session,
        'chat_messages': chat_messages,
        'lang_name':     lang_name,
        'level_display': dict(LESSON_LEVELS).get(session.level, session.level.title()),
    })


@login_required
def my_language_progress(request):
    """Progress dashboard: all languages the user has studied with AI."""
    progress_list        = LessonProgress.objects.filter(user=request.user).order_by('-last_studied')
    all_sessions         = AITutorSession.objects.filter(user=request.user).order_by('-created_at')
    recent_sessions      = all_sessions[:10]
    total_credits_spent  = sum(s.credits_spent for s in all_sessions)
    total_lessons        = sum(p.lessons_completed for p in progress_list)
    total_sessions_count = all_sessions.count()
    return render(request, 'languages/my_progress.html', {
        'progress_list':       progress_list,
        'recent_sessions':     recent_sessions,
        'total_credits_spent': total_credits_spent,
        'total_lessons':       total_lessons,
        'total_sessions':      total_sessions_count,
    })
