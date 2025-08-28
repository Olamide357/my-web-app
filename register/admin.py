# import UserAdmin as BaseUserAdmin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import UserProfile
# Register your models here.

class UserProfileAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'phone', 'wallet_balance', 'is_staff', "is_active")
    list_filter = ("is_staff", "is_active")

    fieldsets = (
        (None, {'fields': ('username', 'email', 'phone', 'wallet_balance', 'password')}),
        (_('Permission'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login',)})
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'phone', 'wallet_balance', 'password', 'confirm_password', 'is_staff', 'is_active'),
        }),
    )

    search_fields = ('username', 'email', 'phone')
    ordering = ('email',)
admin.site.register(UserProfile, UserProfileAdmin)
