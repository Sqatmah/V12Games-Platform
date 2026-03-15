from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'is_staff', 'date_joined']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Profile', {
            'fields': ('avatar', 'bio', 'liked_games'),
        }),
    )
    filter_horizontal = ['liked_games', 'groups', 'user_permissions']