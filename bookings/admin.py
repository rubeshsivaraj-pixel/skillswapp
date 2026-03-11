from django.contrib import admin
from .models import Session, Review

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('skill', 'teacher', 'student', 'date', 'time', 'status')
    list_filter = ('status', 'date')
    search_fields = ('teacher__username', 'student__username', 'skill__name')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('session', 'reviewer', 'reviewee', 'rating')
    list_filter = ('rating',)
    search_fields = ('reviewer__username', 'reviewee__username')
