from django.contrib import admin
from .models import Course, CoursePurchase


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'category', 'credit_cost', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'created_at')
    list_editable = ('is_active', 'credit_cost')
    search_fields = ('title', 'instructor__username')
    readonly_fields = ('created_at',)


@admin.register(CoursePurchase)
class CoursePurchaseAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'credits_spent', 'purchased_at')
    list_filter = ('purchased_at',)
    search_fields = ('user__username', 'course__title')
    readonly_fields = ('purchased_at',)
