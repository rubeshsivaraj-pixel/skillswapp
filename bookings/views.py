from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Session, Review
from skills.models import Skill
from accounts.models import CustomUser
from .forms import SessionRequestForm, ReviewForm

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
            messages.success(request, f'Session request sent to {teacher.username} for {skill.name}!')
            return redirect('dashboard')
    else:
        form = SessionRequestForm()
        
    return render(request, 'bookings/book_session.html', {'form': form, 'teacher': teacher, 'skill': skill})

@login_required
def session_list(request):
    user = request.user
    teaching_sessions = Session.objects.filter(teacher=user).order_by('-date', '-time')
    learning_sessions = Session.objects.filter(student=user).order_by('-date', '-time')
    
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
        messages.success(request, f'Session with {session.student.username} accepted.')
    return redirect('session_list')

@login_required
def reject_session(request, session_id):
    session = get_object_or_404(Session, id=session_id, teacher=request.user)
    if session.status == 'PENDING':
        session.status = 'REJECTED'
        session.save()
        messages.success(request, f'Session with {session.student.username} rejected.')
    return redirect('session_list')

@login_required
def complete_session(request, session_id):
    session = get_object_or_404(Session, id=session_id, teacher=request.user)
    if session.status == 'ACCEPTED':
        session.status = 'COMPLETED'
        session.save()
        messages.success(request, 'Session marked as completed. Waiting for student feedback to process credits.')
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
            
            # Credit logic: Student spends 1, Teacher earns 1
            request.user.credits -= 1
            request.user.save()
            
            session.teacher.credits += 1
            session.teacher.save()
            
            messages.success(request, 'Review submitted successfully! Credits have been exchanged.')
            return redirect('session_list')
    else:
        form = ReviewForm()
        
    return render(request, 'bookings/review_session.html', {'form': form, 'session': session})
