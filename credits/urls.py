from django.urls import path
from . import views

urlpatterns = [
    path('history/', views.credit_history, name='credit_history'),
    path('balance/', views.credit_balance_api, name='credit_balance_api'),
]
