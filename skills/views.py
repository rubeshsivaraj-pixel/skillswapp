from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Skill, UserSkill, VideoTutorial, AudioLesson, SkillDemonstration
from .forms import UserSkillForm, VideoUploadForm, AudioUploadForm

@login_required
def add_skill(request):
    if request.method == 'POST':
        form = UserSkillForm(request.POST)
        if form.is_valid():
            try:
                form.save(user=request.user)
                messages.success(request, 'Skill added successfully!')
                return redirect('dashboard')
            except Exception as e:
                messages.error(request, f'Error adding skill: {e}')
    else:
        form = UserSkillForm()
    
    return render(request, 'skills/add_skill.html', {'form': form})

@login_required
def remove_skill(request, skill_id):
    user_skill = get_object_or_404(UserSkill, id=skill_id, user=request.user)
    if request.method == 'POST':
        user_skill.delete()
        messages.success(request, 'Skill removed.')
        return redirect('dashboard')
    
    return render(request, 'skills/remove_skill_confirm.html', {'user_skill': user_skill})

def skill_marketplace(request):
    skills = Skill.objects.all()
    
    # Filter applied
    search_query = request.GET.get('q', '')
    if search_query:
        skills = skills.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    category_filter = request.GET.get('category', '')
    if category_filter:
        skills = skills.filter(category__icontains=category_filter)
    
    # Find all users who are offering to teach
    teaching_skills = UserSkill.objects.filter(skill_type='TEACH').select_related('user', 'skill')
    if request.user.is_authenticated:
        teaching_skills = teaching_skills.exclude(user=request.user)
    
    # Get videos and audio lessons
    approved_videos = VideoTutorial.objects.filter(status='APPROVED').select_related('user', 'skill').order_by('-created_at')[:12]
    approved_audio = AudioLesson.objects.filter(status='APPROVED').select_related('user', 'skill').order_by('-created_at')[:12]
    
    # Get all skill categories for filter
    categories = Skill.objects.values_list('category', flat=True).exclude(category__isnull=True).distinct()
    
    context = {
        'skills': skills,
        'teaching_skills': teaching_skills,
        'approved_videos': approved_videos,
        'approved_audio': approved_audio,
        'search_query': search_query,
        'categories': categories,
        'category_filter': category_filter,
    }
    return render(request, 'skills/marketplace.html', context)

@login_required
def upload_video(request):
    """Allow users to upload a tutorial video"""
    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save(commit=False)
            video.user = request.user
            video.save()
            messages.success(request, 'Video uploaded successfully! You will earn 10 credits once it is approved.')
            return redirect('upload_video')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field.replace("_", " ").title()}: {error}')
    else:
        form = VideoUploadForm()

    my_videos = VideoTutorial.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'skills/upload_video.html', {'form': form, 'my_videos': my_videos})

@login_required
def upload_audio(request):
    """Allow users to upload an audio lesson"""
    if request.method == 'POST':
        form = AudioUploadForm(request.POST, request.FILES)
        if form.is_valid():
            audio = form.save(commit=False)
            audio.user = request.user
            audio.save()
            messages.success(request, 'Audio lesson uploaded successfully! You will earn 5 credits once it is approved.')
            return redirect('upload_audio')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field.replace("_", " ").title()}: {error}')
    else:
        form = AudioUploadForm()

    my_audio = AudioLesson.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'skills/upload_audio.html', {'form': form, 'my_audio': my_audio})

def video_detail(request, pk):
    """Watch a video — approved for everyone, pending/rejected only for the owner."""
    from django.http import Http404
    video = get_object_or_404(VideoTutorial, pk=pk)
    if video.status != 'APPROVED':
        if not request.user.is_authenticated or request.user != video.user:
            raise Http404
    else:
        VideoTutorial.objects.filter(pk=pk).update(views=video.views + 1)
        video.views += 1
    related = VideoTutorial.objects.filter(
        skill=video.skill, status='APPROVED'
    ).exclude(pk=pk).order_by('-created_at')[:6]
    return render(request, 'skills/video_detail.html', {'video': video, 'related': related})


@login_required
def delete_video(request, pk):
    """Allow the uploader to delete their own video (only if PENDING or REJECTED)"""
    video = get_object_or_404(VideoTutorial, pk=pk, user=request.user)
    if video.status == 'APPROVED':
        messages.error(request, 'Approved videos cannot be deleted.')
        return redirect('upload_video')
    if request.method == 'POST':
        video.video_file.delete(save=False)
        if video.thumbnail:
            video.thumbnail.delete(save=False)
        video.delete()
        messages.success(request, 'Video deleted.')
        return redirect('upload_video')
    return render(request, 'skills/delete_video_confirm.html', {'video': video})


@login_required
def content_library(request):
    """Browse all approved videos and audio lessons"""
    skill_filter = request.GET.get('skill', '')
    search_query = request.GET.get('q', '')
    content_type = request.GET.get('type', 'all')
    
    videos = VideoTutorial.objects.filter(status='APPROVED').select_related('user', 'skill')
    audio = AudioLesson.objects.filter(status='APPROVED').select_related('user', 'skill')
    
    if skill_filter:
        videos = videos.filter(skill__name__icontains=skill_filter)
        audio = audio.filter(skill__name__icontains=skill_filter)
    
    if search_query:
        videos = videos.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query))
        audio = audio.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query))
    
    context = {
        'videos': videos.order_by('-created_at')[:20],
        'audio': audio.order_by('-created_at')[:20],
        'skill_filter': skill_filter,
        'search_query': search_query,
        'content_type': content_type,
        'skills': Skill.objects.all(),
    }
    return render(request, 'skills/content_library.html', context)
