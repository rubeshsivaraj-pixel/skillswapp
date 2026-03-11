from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'credits', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('bio', 'credits')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('bio', 'credits')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
