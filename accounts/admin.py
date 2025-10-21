"""
Admin configuration for accounts app.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, UserProfile, BankAccount, SecuritySettings, LoginAttempt


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_verified', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'is_verified', 'two_factor_enabled')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('username', 'first_name', 'last_name', 'phone_number', 'date_of_birth')}),
        (_('Verification'), {'fields': ('is_verified', 'is_phone_verified', 'two_factor_enabled')}),
        (_('Security'), {'fields': ('last_login_ip', 'failed_login_attempts', 'account_locked_until')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'kyc_status', 'country', 'currency', 'created_at')
    list_filter = ('kyc_status', 'gender', 'country', 'currency')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('kyc_submitted_at', 'kyc_verified_at', 'created_at', 'updated_at')
    
    fieldsets = (
        (_('Basic Info'), {'fields': ('user', 'gender', 'address', 'city', 'state', 'country', 'postal_code')}),
        (_('KYC Information'), {'fields': ('id_type', 'id_number', 'id_document', 'proof_of_address', 'kyc_status', 'kyc_notes')}),
        (_('Preferences'), {'fields': ('currency', 'language', 'timezone')}),
        (_('Timestamps'), {'fields': ('kyc_submitted_at', 'kyc_verified_at', 'created_at', 'updated_at')}),
    )


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ('account_number', 'account_name', 'user', 'account_type', 'currency', 'balance', 'status')
    list_filter = ('account_type', 'currency', 'status', 'is_default')
    search_fields = ('account_number', 'account_name', 'user__email')
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    fieldsets = (
        (_('Account Info'), {'fields': ('user', 'account_number', 'account_name', 'account_type', 'currency')}),
        (_('Balances'), {'fields': ('balance', 'available_balance', 'frozen_balance')}),
        (_('Limits'), {'fields': ('daily_limit', 'single_transaction_limit')}),
        (_('Status'), {'fields': ('status', 'is_default')}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(SecuritySettings)
class SecuritySettingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'login_notifications', 'transaction_notifications', 'require_otp_for_transactions')
    list_filter = ('login_notifications', 'transaction_notifications', 'require_otp_for_transactions')
    search_fields = ('user__email',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    list_display = ('email', 'ip_address', 'success', 'failure_reason', 'timestamp')
    list_filter = ('success', 'timestamp')
    search_fields = ('email', 'ip_address')
    readonly_fields = ('timestamp',)
    
    def has_add_permission(self, request):
        return False