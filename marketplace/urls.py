from django.urls import path
from . import views

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('purchase/<int:course_id>/', views.purchase_course, name='purchase_course'),
    path('history/', views.purchase_history, name='purchase_history'),
    path('ai-chat/', views.ai_language_chat, name='ai_language_chat'),
    path('ai-mentors/', views.ai_mentor_match, name='ai_mentor_match'),
]
