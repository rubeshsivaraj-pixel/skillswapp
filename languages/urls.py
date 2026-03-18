from django.urls import path
from . import views

urlpatterns = [
    # Human-tutor marketplace
    path('',                                views.language_marketplace,  name='language_marketplace'),
    path('mine/',                           views.my_languages,          name='my_languages'),
    path('add/',                            views.add_language,          name='add_language'),
    path('book/<int:teacher_id>/',          views.book_language_session, name='book_language_session'),
    path('sessions/',                       views.my_lang_sessions,      name='my_lang_sessions'),

    # AI tutor
    path('ai/',                             views.ai_tutor_home,         name='ai_tutor_home'),
    path('ai/<str:lang_code>/',             views.lesson_modules,        name='lesson_modules'),
    path('ai/<str:lang_code>/start/',       views.start_ai_session,      name='start_ai_session'),
    path('ai/session/<int:session_id>/',    views.ai_lesson_chat,        name='ai_lesson_chat'),
    path('progress/',                       views.my_language_progress,  name='my_language_progress'),
]
