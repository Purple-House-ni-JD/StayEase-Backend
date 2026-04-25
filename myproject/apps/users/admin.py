from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, OAuthAccount


class OAuthAccountInline(admin.TabularInline):
    model = OAuthAccount
    extra = 0
    readonly_fields = ['provider', 'provider_user_id', 'provider_avatar_url', 'created_at']
    can_delete = False


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'first_name', 'last_name', 'role', 'is_active', 'date_joined']
    list_filter = ['role', 'is_active']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    inlines = [OAuthAccountInline]
    fieldsets = UserAdmin.fieldsets + (
        ('StayEase', {'fields': ('role', 'phone_number', 'avatar_url')}),
    )


@admin.register(OAuthAccount)
class OAuthAccountAdmin(admin.ModelAdmin):
    list_display = ['user', 'provider', 'provider_user_id', 'created_at']
    list_filter = ['provider']
    search_fields = ['user__email', 'provider_user_id']
    readonly_fields = ['created_at']