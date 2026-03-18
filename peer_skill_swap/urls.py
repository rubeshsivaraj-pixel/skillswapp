"""
URL configuration for peer_skill_swap project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

# Admin site branding
admin.site.site_header = 'SkillSwap Administration'
admin.site.site_title = 'SkillSwap Admin'
admin.site.index_title = 'Platform Management Dashboard'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('call/<str:username>/', views.video_call, name='video_call'),
    path('accounts/', include('accounts.urls')),
    path('skills/', include('skills.urls')),
    path('messages/', include('messaging.urls')),
    path('sessions/', include('bookings.urls')),
    path('notifications/', include('notifications.urls')),
    path('credits/', include('credits.urls')),
    path('friends/', include('friends.urls')),
    path('languages/', include('languages.urls')),
    path('marketplace/', include('marketplace.urls')),
]

# Media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
