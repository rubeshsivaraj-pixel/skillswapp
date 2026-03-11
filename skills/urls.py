from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.add_skill, name='add_skill'),
    path('remove/<int:skill_id>/', views.remove_skill, name='remove_skill'),
    path('marketplace/', views.skill_marketplace, name='skill_marketplace'),
]
