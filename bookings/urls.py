from django.urls import path
from . import views

urlpatterns = [
    path('', views.session_list, name='session_list'),
    path('book/<str:teacher_username>/<int:skill_id>/', views.book_session, name='book_session'),
    path('<int:session_id>/accept/', views.accept_session, name='accept_session'),
    path('<int:session_id>/reject/', views.reject_session, name='reject_session'),
    path('<int:session_id>/complete/', views.complete_session, name='complete_session'),
    path('<int:session_id>/review/', views.review_session, name='review_session'),
]
