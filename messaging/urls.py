from django.urls import path
from . import views

urlpatterns = [
    path('', views.inbox, name='inbox'),
    path('chat/<str:username>/', views.chat, name='chat'),
    path('send/<str:username>/', views.send_message_api, name='send_message_api'),
]
