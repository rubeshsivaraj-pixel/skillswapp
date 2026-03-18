from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.add_skill, name='add_skill'),
    path('remove/<int:skill_id>/', views.remove_skill, name='remove_skill'),
    path('marketplace/', views.skill_marketplace, name='skill_marketplace'),
    path('upload/video/', views.upload_video, name='upload_video'),
    path('upload/audio/', views.upload_audio, name='upload_audio'),
    path('library/', views.content_library, name='content_library'),
    path('video/<int:pk>/', views.video_detail, name='video_detail'),
    path('video/<int:pk>/delete/', views.delete_video, name='delete_video'),
]
