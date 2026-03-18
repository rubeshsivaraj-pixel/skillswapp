from django import forms
import os
from .models import UserSkill, Skill, VideoTutorial, AudioLesson

class UserSkillForm(forms.ModelForm):
    skill_name = forms.CharField(max_length=100, help_text="Enter a skill name to add. It will be created if it doesn't exist.")

    class Meta:
        model = UserSkill
        fields = ['skill_type', 'proficiency']
        widgets = {
            'proficiency': forms.Select(choices=[
                ('', 'Select Proficiency Level'),
                ('Beginner', 'Beginner'),
                ('Intermediate', 'Intermediate'),
                ('Expert', 'Expert'),
            ])
        }

    def save(self, user, commit=True):
        skill_name = self.cleaned_data.get('skill_name').strip().title()
        skill, created = Skill.objects.get_or_create(name=skill_name)
        
        user_skill = super().save(commit=False)
        user_skill.user = user
        user_skill.skill = skill
        
        if commit:
            user_skill.save()
        return user_skill


class VideoUploadForm(forms.ModelForm):
    class Meta:
        model = VideoTutorial
        fields = ['title', 'description', 'skill', 'video_file', 'thumbnail']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Enter a descriptive title for your tutorial video'}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe what learners will gain from this video... (optional)'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].required = False
        self.fields['thumbnail'].required = False
    
    def clean_video_file(self):
        video = self.cleaned_data.get('video_file')
        if video:
            # Use broad content_type check and extension fallback
            allowed_types = [
                'video/mp4', 'video/mpeg', 'video/webm', 'video/ogg',
                'video/quicktime',       # .mov
                'video/x-msvideo',       # .avi
                'video/x-matroska',      # .mkv
                'video/x-ms-wmv',        # .wmv
                'video/3gpp',            # .3gp
                'application/octet-stream',  # generic binary (some browsers)
            ]
            allowed_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.wmv', '.mpeg', '.mpg', '.3gp']
            max_size = 500 * 1024 * 1024  # 500MB

            content_type = getattr(video, 'content_type', '')
            ext = os.path.splitext(video.name)[1].lower() if video.name else ''

            if content_type and content_type not in allowed_types and ext not in allowed_extensions:
                raise forms.ValidationError(
                    f'Unsupported file type ({content_type}). Allowed: MP4, AVI, MOV, MKV, WebM.'
                )

            if video.size > max_size:
                raise forms.ValidationError('Video size must not exceed 500MB.')
        return video


class AudioUploadForm(forms.ModelForm):
    class Meta:
        model = AudioLesson
        fields = ['title', 'description', 'skill', 'audio_file']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Enter a descriptive title for your audio lesson'}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe what learners will gain from this audio lesson... (optional)'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].required = False
    
    def clean_audio_file(self):
        audio = self.cleaned_data.get('audio_file')
        if audio:
            allowed_types = [
                'audio/mpeg', 'audio/mp3',   # .mp3
                'audio/ogg',                 # .ogg
                'audio/wav', 'audio/x-wav', 'audio/wave',  # .wav
                'audio/mp4', 'audio/x-m4a', 'audio/m4a',  # .m4a
                'audio/aac',                 # .aac
                'audio/flac',                # .flac
                'audio/webm',                # .webm audio
                'application/octet-stream',  # generic binary
            ]
            allowed_extensions = ['.mp3', '.ogg', '.wav', '.m4a', '.aac', '.flac', '.webm', '.wma']
            max_size = 100 * 1024 * 1024  # 100MB

            content_type = getattr(audio, 'content_type', '')
            ext = os.path.splitext(audio.name)[1].lower() if audio.name else ''

            if content_type and content_type not in allowed_types and ext not in allowed_extensions:
                raise forms.ValidationError(
                    f'Unsupported file type ({content_type}). Allowed: MP3, WAV, OGG, M4A, AAC, FLAC.'
                )

            if audio.size > max_size:
                raise forms.ValidationError('Audio size must not exceed 100MB.')
        return audio
