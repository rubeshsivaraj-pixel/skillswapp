from django import forms
from .models import UserSkill, Skill

class UserSkillForm(forms.ModelForm):
    skill_name = forms.CharField(max_length=100, help_text="Enter a skill name to add. It will be created if it doesn't exist.")

    class Meta:
        model = UserSkill
        fields = ['skill_type', 'proficiency']

    def save(self, user, commit=True):
        skill_name = self.cleaned_data.get('skill_name').strip().title()
        skill, created = Skill.objects.get_or_create(name=skill_name)
        
        user_skill = super().save(commit=False)
        user_skill.user = user
        user_skill.skill = skill
        
        if commit:
            user_skill.save()
        return user_skill
