from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Skill, UserSkill
from .forms import UserSkillForm

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
    # Find all users who are offering to teach
    teaching_skills = UserSkill.objects.filter(skill_type='TEACH').select_related('user', 'skill')
    
    context = {
        'skills': skills,
        'teaching_skills': teaching_skills,
    }
    return render(request, 'skills/marketplace.html', context)
