"""
Custom User model and account management for SecureBank.
Enhanced security with proper user roles and account types.
"""

import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from decimal import Decimal


class User(AbstractUser):
    """
    Custom user model with enhanced security features.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_('email address'), unique=True)
    phone_number = models.CharField(
        _('phone number'),
        max_length=15,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message=_("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
            )
        ],
        blank=True,
        null=True
    )
    date_of_birth = models.DateField(_('date of birth'), null=True, blank=True)
    is_verified = models.BooleanField(_('email verified'), default=False)
    is_phone_verified = models.BooleanField(_('phone verified'), default=False)
    two_factor_enabled = models.BooleanField(_('2FA enabled'), default=False)
    last_login_ip = models.GenericIPAddressField(_('last login IP'), null=True, blank=True)
    failed_login_attempts = models.PositiveIntegerField(_('failed login attempts'), default=0)
    account_locked_until = models.DateTimeField(_('account locked until'), null=True, blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        db_table = 'accounts_user'

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def is_account_locked(self):
        from django.utils import timezone
        return self.account_locked_until and self.account_locked_until > timezone.now()


class UserProfile(models.Model):
    """
    Extended user profile with KYC information.
    """
    GENDER_CHOICES = [
        ('M', _('Male')),
        ('F', _('Female')),
        ('O', _('Other')),
    ]

    ID_TYPE_CHOICES = [
        ('NIN', _('National ID')),
        ('PASSPORT', _('Passport')),
        ('DRIVERS_LICENSE', _('Driver\'s License')),
        ('VOTERS_CARD', _('Voter\'s Card')),
    ]

    KYC_STATUS_CHOICES = [
        ('PENDING', _('Pending')),
        ('VERIFIED', _('Verified')),
        ('REJECTED', _('Rejected')),
        ('REVIEW', _('Under Review')),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    gender = models.CharField(_('gender'), max_length=1, choices=GENDER_CHOICES, blank=True)
    address = models.TextField(_('address'), blank=True)
    city = models.CharField(_('city'), max_length=100, blank=True)
    state = models.CharField(_('state'), max_length=100, blank=True)
    country = models.CharField(_('country'), max_length=100, blank=True)
    postal_code = models.CharField(_('postal code'), max_length=20, blank=True)
    
    # KYC Information
    id_type = models.CharField(_('ID type'), max_length=20, choices=ID_TYPE_CHOICES, blank=True)
    id_number = models.CharField(_('ID number'), max_length=50, blank=True)
    id_document = models.ImageField(_('ID document'), upload_to='kyc_documents/', null=True, blank=True)
    proof_of_address = models.ImageField(_('proof of address'), upload_to='address_documents/', null=True, blank=True)
    kyc_status = models.CharField(_('KYC status'), max_length=20, choices=KYC_STATUS_CHOICES, default='PENDING')
    kyc_submitted_at = models.DateTimeField(_('KYC submitted at'), null=True, blank=True)
    kyc_verified_at = models.DateTimeField(_('KYC verified at'), null=True, blank=True)
    kyc_notes = models.TextField(_('KYC notes'), blank=True)

    # Preferences
    currency = models.CharField(_('preferred currency'), max_length=3, default='NGN')
    language = models.CharField(_('preferred language'), max_length=10, default='en')
    timezone = models.CharField(_('timezone'), max_length=50, default='UTC')
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('User Profile')
        verbose_name_plural = _('User Profiles')
        db_table = 'accounts_user_profile'

    def __str__(self):
        return f"{self.user.email} - Profile"

    @property
    def is_kyc_verified(self):
        return self.kyc_status == 'VERIFIED'


class BankAccount(models.Model):
    """
    User bank accounts with different account types.
    """
    ACCOUNT_TYPE_CHOICES = [
        ('SAVINGS', _('Savings Account')),
        ('CURRENT', _('Current Account')),
        ('FIXED_DEPOSIT', _('Fixed Deposit')),
        ('CRYPTO', _('Crypto Wallet')),
        ('BUSINESS', _('Business Account')),
    ]

    ACCOUNT_STATUS_CHOICES = [
        ('ACTIVE', _('Active')),
        ('FROZEN', _('Frozen')),
        ('CLOSED', _('Closed')),
        ('SUSPENDED', _('Suspended')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accounts')
    account_number = models.CharField(_('account number'), max_length=20, unique=True)
    account_name = models.CharField(_('account name'), max_length=100)
    account_type = models.CharField(_('account type'), max_length=20, choices=ACCOUNT_TYPE_CHOICES)
    balance = models.DecimalField(_('balance'), max_digits=15, decimal_places=2, default=Decimal('0.00'))
    available_balance = models.DecimalField(_('available balance'), max_digits=15, decimal_places=2, default=Decimal('0.00'))
    frozen_balance = models.DecimalField(_('frozen balance'), max_digits=15, decimal_places=2, default=Decimal('0.00'))
    currency = models.CharField(_('currency'), max_length=3, default='NGN')
    status = models.CharField(_('status'), max_length=20, choices=ACCOUNT_STATUS_CHOICES, default='ACTIVE')
    is_default = models.BooleanField(_('default account'), default=False)
    daily_limit = models.DecimalField(_('daily limit'), max_digits=15, decimal_places=2, default=Decimal('500000.00'))
    single_transaction_limit = models.DecimalField(_('single transaction limit'), max_digits=15, decimal_places=2, default=Decimal('100000.00'))
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('Bank Account')
        verbose_name_plural = _('Bank Accounts')
        db_table = 'accounts_bank_account'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.account_number} - {self.account_name}"

    def save(self, *args, **kwargs):
        if not self.account_number:
            self.account_number = self.generate_account_number()
        super().save(*args, **kwargs)

    def generate_account_number(self):
        """Generate unique account number."""
        import random
        while True:
            number = f"209{random.randint(1000000000, 9999999999)}"
            if not BankAccount.objects.filter(account_number=number).exists():
                return number

    @property
    def is_active(self):
        return self.status == 'ACTIVE'

    def can_withdraw(self, amount):
        """Check if user can withdraw specified amount."""
        return (
            self.is_active and
            amount <= self.available_balance and
            amount <= self.single_transaction_limit
        )


class SecuritySettings(models.Model):
    """
    User security settings and preferences.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='security_settings')
    
    # Login Security
    login_notifications = models.BooleanField(_('login notifications'), default=True)
    transaction_notifications = models.BooleanField(_('transaction notifications'), default=True)
    email_alerts = models.BooleanField(_('email alerts'), default=True)
    sms_alerts = models.BooleanField(_('SMS alerts'), default=False)
    
    # Transaction Security
    require_otp_for_transactions = models.BooleanField(_('require OTP for transactions'), default=True)
    transaction_threshold = models.DecimalField(_('transaction threshold'), max_digits=15, decimal_places=2, default=Decimal('10000.00'))
    
    # Session Security
    auto_logout_time = models.PositiveIntegerField(_('auto logout time (minutes)'), default=60)
    concurrent_sessions = models.BooleanField(_('allow concurrent sessions'), default=False)
    
    # Device Management
    trusted_devices_only = models.BooleanField(_('trusted devices only'), default=False)
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('Security Settings')
        verbose_name_plural = _('Security Settings')
        db_table = 'accounts_security_settings'

    def __str__(self):
        return f"{self.user.email} - Security Settings"


class LoginAttempt(models.Model):
    """
    Track login attempts for security monitoring.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_attempts', null=True, blank=True)
    email = models.EmailField(_('email'))
    ip_address = models.GenericIPAddressField(_('IP address'))
    user_agent = models.TextField(_('user agent'), blank=True)
    success = models.BooleanField(_('success'), default=False)
    failure_reason = models.CharField(_('failure reason'), max_length=100, blank=True)
    timestamp = models.DateTimeField(_('timestamp'), auto_now_add=True)

    class Meta:
        verbose_name = _('Login Attempt')
        verbose_name_plural = _('Login Attempts')
        db_table = 'accounts_login_attempt'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.email} - {self.timestamp} - {'Success' if self.success else 'Failed'}"