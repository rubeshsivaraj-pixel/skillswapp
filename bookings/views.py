from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg
from .models import Session, Review
from skills.models import Skill
from accounts.models import CustomUser
from .forms import SessionRequestForm, ReviewForm
from notifications.models import Notification
from credits.views import award_credits
from leaderboard.models import Leaderboard

@login_required
def book_session(request, teacher_username, skill_id):
    teacher = get_object_or_404(CustomUser, username=teacher_username)
    skill = get_object_or_404(Skill, id=skill_id)
    
    # Check if student has credits
    if request.user.credits < 1:
        messages.error(request, 'You do not have enough credits to book a session.')
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = SessionRequestForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.teacher = teacher
            session.student = request.user
            session.skill = skill
            session.save()
            
            # Notify the teacher
            Notification.objects.create(
                user=teacher,
                notification_type='SESSION_REQUEST',
                title=f'New session request from {request.user.username}',
                message=f'{request.user.username} wants to book a session with you for {skill.name} on {form.cleaned_data["date"]}.'
            )
            
            messages.success(request, f'Session request sent to {teacher.username} for {skill.name}!')
            return redirect('dashboard')
    else:
        form = SessionRequestForm()
        
    return render(request, 'bookings/book_session.html', {'form': form, 'teacher': teacher, 'skill': skill})

@login_required
def session_list(request):
    user = request.user
    teaching_sessions = Session.objects.filter(teacher=user).order_by('-date', '-time').select_related('student', 'skill')
    learning_sessions = Session.objects.filter(student=user).order_by('-date', '-time').select_related('teacher', 'skill')
    
    return render(request, 'bookings/my_sessions.html', {
        'teaching_sessions': teaching_sessions,
        'learning_sessions': learning_sessions
    })

@login_required
def accept_session(request, session_id):
    session = get_object_or_404(Session, id=session_id, teacher=request.user)
    if session.status == 'PENDING':
        session.status = 'ACCEPTED'
        session.save()
        
        # Notify the student
        Notification.objects.create(
            user=session.student,
            notification_type='SESSION_ACCEPTED',
            title=f'Session accepted by {request.user.username}',
            message=f'{request.user.username} accepted your session request for {session.skill.name} on {session.date}.'
        )
        
        messages.success(request, f'Session with {session.student.username} accepted.')
    return redirect('session_list')

@login_required
def reject_session(request, session_id):
    session = get_object_or_404(Session, id=session_id, teacher=request.user)
    if session.status == 'PENDING':
        session.status = 'REJECTED'
        session.save()
        
        # Notify the student
        Notification.objects.create(
            user=session.student,
            notification_type='SESSION_REJECTED',
            title=f'Session rejected by {request.user.username}',
            message=f'{request.user.username} rejected your session request for {session.skill.name}.'
        )
        
        messages.success(request, f'Session with {session.student.username} rejected.')
    return redirect('session_list')

@login_required
def complete_session(request, session_id):
    session = get_object_or_404(Session, id=session_id, teacher=request.user)
    if session.status == 'ACCEPTED':
        session.status = 'COMPLETED'
        session.save()
        
        # Award credits to teacher for teaching the session (+15 credits)
        award_credits(
            session.teacher,
            'TEACH_SESSION',
            15,
            f'Taught {session.skill.name} to {session.student.username}',
            'session',
            session.id
        )
        
        # Update teacher's leaderboard stats
        leaderboard, _ = Leaderboard.objects.get_or_create(user=session.teacher)
        leaderboard.sessions_taught += 1
        leaderboard.total_credits_earned += 15
        leaderboard.current_credits = session.teacher.credits
        leaderboard.save()
        
        # Update teacher's total_sessions_taught
        session.teacher.total_sessions_taught += 1
        session.teacher.save()
        
        # Notify the teacher about credits
        Notification.objects.create(
            user=session.teacher,
            notification_type='CREDITS_EARNED',
            title='+15 Credits Earned!',
            message=f'You earned 15 credits for teaching {session.skill.name} to {session.student.username}!'
        )
        
        # Notify the student
        Notification.objects.create(
            user=session.student,
            notification_type='SESSION_ACCEPTED',
            title=f'Session with {session.teacher.username} completed',
            message=f'Your {session.skill.name} session with {session.teacher.username} has been marked complete. Please leave a review!'
        )
        
        messages.success(request, f'Session completed! You earned 15 credits for teaching.')
    return redirect('session_list')

@login_required
def review_session(request, session_id):
    session = get_object_or_404(Session, id=session_id, student=request.user, status='COMPLETED')
    
    if hasattr(session, 'review'):
        messages.info(request, 'You have already reviewed this session.')
        return redirect('session_list')
        
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.session = session
            review.reviewer = request.user
            review.reviewee = session.teacher
            review.save()
            
            # Update reviewee's average rating
            avg = Review.objects.filter(reviewee=session.teacher).aggregate(Avg('rating'))['rating__avg']
            session.teacher.average_rating = round(avg, 1) if avg else 0
            session.teacher.save()
            
            # Update leaderboard for teacher
            leaderboard, _ = Leaderboard.objects.get_or_create(user=session.teacher)
            leaderboard.average_rating = round(avg, 1) if avg else 0
            leaderboard.total_reviews += 1
            leaderboard.save()
            
            # Update learner stats
            learner_leaderboard, _ = Leaderboard.objects.get_or_create(user=request.user)
            learner_leaderboard.sessions_learned += 1
            learner_leaderboard.save()
            request.user.total_sessions_learned += 1
            request.user.save()
            
            # Notify teacher about the review
            Notification.objects.create(
                user=session.teacher,
                notification_type='REVIEW_RECEIVED',
                title=f'New review from {request.user.username}',
                message=f'{request.user.username} gave you {review.rating}/5 stars for {session.skill.name}: "{review.comment or "No comment"}"'
            )
            
            messages.success(request, f'Review submitted! {session.teacher.username} received your feedback.')
            return redirect('session_list')
    else:
        form = ReviewForm()
        
    return render(request, 'bookings/review_session.html', {'form': form, 'session': session})
