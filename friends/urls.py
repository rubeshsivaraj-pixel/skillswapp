from django.urls import path
from . import views

urlpatterns = [
    path('', views.friend_list, name='friend_list'),
    path('request/<str:username>/', views.send_request, name='send_friend_request'),
    path('accept/<int:request_id>/', views.accept_request, name='accept_friend_request'),
    path('reject/<int:request_id>/', views.reject_request, name='reject_friend_request'),
    path('unfriend/<str:username>/', views.unfriend, name='unfriend'),
    path('status/<str:username>/', views.friendship_status_api, name='friendship_status_api'),
]
