from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from skills.models import UserSkill, Skill

def home(request):
    if request.user.is_authenticated:
        return render(request, 'home_authenticated.html')
    return render(request, 'home.html')

@login_required
def dashboard(request):
    user = request.user
    
    # User's skills
    teaching_skills = UserSkill.objects.filter(user=user, skill_type='TEACH')
    learning_skills = UserSkill.objects.filter(user=user, skill_type='LEARN')
    
    # Matching algorithm
    # 1. Get IDs of skills the user wants to learn
    wanted_skill_ids = learning_skills.values_list('skill_id', flat=True)
    
    # 2. Find other users who TEACH those skills (exclude self)
    matches_raw = UserSkill.objects.filter(
        skill_id__in=wanted_skill_ids, 
        skill_type='TEACH'
    ).exclude(user=user).select_related('user', 'skill')
    
    # Ensure distinct users / structure the matches for display
    # Group by User to avoid showing the same user multiple times if they teach multiple wanted skills
    matched_users = {}
    for match in matches_raw:
        if match.user not in matched_users:
            matched_users[match.user] = []
        matched_users[match.user].append(match.skill)
    
    context = {
        'teaching_skills': teaching_skills,
        'learning_skills': learning_skills,
        'matched_users': matched_users,  # dict of User: [List of Skills they teach that I want]
    }
    return render(request, 'dashboard.html', context)
