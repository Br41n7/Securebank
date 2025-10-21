"""
Additional services models for SecureBank.
Handles airtime top-up, school fees, bill payments, and other services.
"""

import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from decimal import Decimal

from accounts.models import BankAccount

User = get_user_model()


class ServiceProvider(models.Model):
    """
    Service providers for various payment services.
    """
    SERVICE_TYPE_CHOICES = [
        ('AIRTIME', _('Airtime')),
        ('INTERNET', _('Internet')),
        ('ELECTRICITY', _('Electricity')),
        ('TV_SUBSCRIPTION', _('TV Subscription')),
        ('SCHOOL_FEES', _('School Fees')),
        ('WATER', _('Water Bill')),
        ('GAS', _('Gas Bill')),
        ('INSURANCE', _('Insurance')),
        ('TAX', _('Tax Payment')),
    ]

    name = models.CharField(_('provider name'), max_length=200)
    service_type = models.CharField(_('service type'), max_length=20, choices=SERVICE_TYPE_CHOICES)
    code = models.CharField(_('provider code'), max_length=50, unique=True)
    logo = models.ImageField(_('logo'), upload_to='provider_logos/', null=True, blank=True)
    description = models.TextField(_('description'), blank=True)
    website = models.URLField(_('website'), blank=True)
    support_contact = models.CharField(_('support contact'), max_length=100, blank=True)
    is_active = models.BooleanField(_('active'), default=True)
    
    # Service charges
    service_charge = models.DecimalField(_('service charge'), max_digits=10, decimal_places=2, default=Decimal('0.00'))
    charge_type = models.CharField(_('charge type'), max_length=10, choices=[
        ('FIXED', _('Fixed')),
        ('PERCENTAGE', _('Percentage')),
    ], default='FIXED')
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('Service Provider')
        verbose_name_plural = _('Service Providers')
        db_table = 'services_provider'

    def __str__(self):
        return f"{self.name} ({self.service_type})"


class AirtimeTopUp(models.Model):
    """
    Airtime top-up transactions.
    """
    STATUS_CHOICES = [
        ('PENDING', _('Pending')),
        ('PROCESSING', _('Processing')),
        ('COMPLETED', _('Completed')),
        ('FAILED', _('Failed')),
        ('REFUNDED', _('Refunded')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference = models.CharField(_('transaction reference'), max_length=50, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='airtime_topups')
    account = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name='airtime_topups')
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name='airtime_topups')
    
    # Recipient details
    phone_number = models.CharField(_('phone number'), max_length=15)
    network = models.CharField(_('network'), max_length=50)
    
    # Transaction details
    amount = models.DecimalField(_('amount'), max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('50.00'))])
    service_charge = models.DecimalField(_('service charge'), max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(_('total amount'), max_digits=10, decimal_places=2)
    
    # Status
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='PENDING')
    provider_reference = models.CharField(_('provider reference'), max_length=100, blank=True)
    
    # Metadata
    ip_address = models.GenericIPAddressField(_('IP address'), null=True, blank=True)
    user_agent = models.TextField(_('user agent'), blank=True)
    notes = models.TextField(_('notes'), blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    processed_at = models.DateTimeField(_('processed at'), null=True, blank=True)
    completed_at = models.DateTimeField(_('completed at'), null=True, blank=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('Airtime Top-up')
        verbose_name_plural = _('Airtime Top-ups')
        db_table = 'services_airtime_topup'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reference} - {self.phone_number} - {self.amount}"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = self.generate_reference()
        
        # Calculate service charge and total
        if self.provider.charge_type == 'PERCENTAGE':
            self.service_charge = (self.amount * self.provider.service_charge) / 100
        else:
            self.service_charge = self.provider.service_charge
        
        self.total_amount = self.amount + self.service_charge
        
        super().save(*args, **kwargs)

    def generate_reference(self):
        """Generate unique transaction reference."""
        import random
        import string
        
        while True:
            prefix = "AIR"
            timestamp = str(int(self.created_at.timestamp() * 1000)) if self.created_at else str(int(uuid.uuid4().int)[:10])
            random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            reference = f"{prefix}{timestamp}{random_str}"
            
            if not AirtimeTopUp.objects.filter(reference=reference).exists():
                return reference


class BillPayment(models.Model):
    """
    General bill payment transactions.
    """
    BILL_TYPE_CHOICES = [
        ('ELECTRICITY', _('Electricity')),
        ('WATER', _('Water')),
        ('GAS', _('Gas')),
        ('INTERNET', _('Internet')),
        ('TV_SUBSCRIPTION', _('TV Subscription')),
        ('INSURANCE', _('Insurance')),
        ('TAX', _('Tax')),
        ('OTHER', _('Other')),
    ]

    STATUS_CHOICES = [
        ('PENDING', _('Pending')),
        ('PROCESSING', _('Processing')),
        ('COMPLETED', _('Completed')),
        ('FAILED', _('Failed')),
        ('REFUNDED', _('Refunded')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference = models.CharField(_('transaction reference'), max_length=50, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bill_payments')
    account = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name='bill_payments')
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name='bill_payments')
    
    # Bill details
    bill_type = models.CharField(_('bill type'), max_length=20, choices=BILL_TYPE_CHOICES)
    customer_id = models.CharField(_('customer ID'), max_length=100)
    customer_name = models.CharField(_('customer name'), max_length=200)
    meter_number = models.CharField(_('meter number'), max_length=100, blank=True)
    account_number = models.CharField(_('account number'), max_length=100, blank=True)
    
    # Transaction details
    amount = models.DecimalField(_('amount'), max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('100.00'))])
    service_charge = models.DecimalField(_('service charge'), max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(_('total amount'), max_digits=10, decimal_places=2)
    
    # Status
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='PENDING')
    provider_reference = models.CharField(_('provider reference'), max_length=100, blank=True)
    token = models.CharField(_('token'), max_length=200, blank=True)  # For electricity tokens
    
    # Metadata
    ip_address = models.GenericIPAddressField(_('IP address'), null=True, blank=True)
    user_agent = models.TextField(_('user agent'), blank=True)
    notes = models.TextField(_('notes'), blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    processed_at = models.DateTimeField(_('processed at'), null=True, blank=True)
    completed_at = models.DateTimeField(_('completed at'), null=True, blank=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('Bill Payment')
        verbose_name_plural = _('Bill Payments')
        db_table = 'services_bill_payment'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reference} - {self.bill_type} - {self.customer_name}"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = self.generate_reference()
        
        # Calculate service charge and total
        if self.provider.charge_type == 'PERCENTAGE':
            self.service_charge = (self.amount * self.provider.service_charge) / 100
        else:
            self.service_charge = self.provider.service_charge
        
        self.total_amount = self.amount + self.service_charge
        
        super().save(*args, **kwargs)

    def generate_reference(self):
        """Generate unique transaction reference."""
        import random
        import string
        
        while True:
            prefix = "BIL"
            timestamp = str(int(self.created_at.timestamp() * 1000)) if self.created_at else str(int(uuid.uuid4().int)[:10])
            random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            reference = f"{prefix}{timestamp}{random_str}"
            
            if not BillPayment.objects.filter(reference=reference).exists():
                return reference


class SchoolFeePayment(models.Model):
    """
    School fee payment transactions.
    """
    PAYMENT_TYPE_CHOICES = [
        ('TUITION', _('Tuition Fee')),
        ('ACCOMMODATION', _('Accommodation')),
        ('LAB_FEES', _('Lab Fees')),
        ('LIBRARY', _('Library Fees')),
        ('SPORTS', _('Sports Fees')),
        ('EXAMINATION', _('Examination Fees')),
        ('OTHER', _('Other')),
    ]

    STATUS_CHOICES = [
        ('PENDING', _('Pending')),
        ('PROCESSING', _('Processing')),
        ('COMPLETED', _('Completed')),
        ('FAILED', _('Failed')),
        ('REFUNDED', _('Refunded')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference = models.CharField(_('transaction reference'), max_length=50, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='school_fee_payments')
    account = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name='school_fee_payments')
    
    # School details
    school_name = models.CharField(_('school name'), max_length=200)
    school_code = models.CharField(_('school code'), max_length=50, blank=True)
    student_name = models.CharField(_('student name'), max_length=200)
    student_id = models.CharField(_('student ID'), max_length=100)
    class_grade = models.CharField(_('class/grade'), max_length=50, blank=True)
    academic_session = models.CharField(_('academic session'), max_length=50)
    
    # Payment details
    payment_type = models.CharField(_('payment type'), max_length=20, choices=PAYMENT_TYPE_CHOICES)
    amount = models.DecimalField(_('amount'), max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('1000.00'))])
    service_charge = models.DecimalField(_('service charge'), max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(_('total amount'), max_digits=10, decimal_places=2)
    
    # Status
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='PENDING')
    receipt_number = models.CharField(_('receipt number'), max_length=100, blank=True)
    
    # Metadata
    ip_address = models.GenericIPAddressField(_('IP address'), null=True, blank=True)
    user_agent = models.TextField(_('user agent'), blank=True)
    notes = models.TextField(_('notes'), blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    processed_at = models.DateTimeField(_('processed at'), null=True, blank=True)
    completed_at = models.DateTimeField(_('completed at'), null=True, blank=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('School Fee Payment')
        verbose_name_plural = _('School Fee Payments')
        db_table = 'services_school_fee_payment'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reference} - {self.school_name} - {self.student_name}"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = self.generate_reference()
        
        # Calculate service charge and total
        self.service_charge = Decimal('50.00')  # Fixed service charge for school fees
        self.total_amount = self.amount + self.service_charge
        
        super().save(*args, **kwargs)

    def generate_reference(self):
        """Generate unique transaction reference."""
        import random
        import string
        
        while True:
            prefix = "SCH"
            timestamp = str(int(self.created_at.timestamp() * 1000)) if self.created_at else str(int(uuid.uuid4().int)[:10])
            random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            reference = f"{prefix}{timestamp}{random_str}"
            
            if not SchoolFeePayment.objects.filter(reference=reference).exists():
                return reference


class ServiceTransaction(models.Model):
    """
    Generic service transaction for tracking all service payments.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='service_transactions')
    service_type = models.CharField(_('service type'), max_length=20)
    service_id = models.CharField(_('service ID'), max_length=50)
    amount = models.DecimalField(_('amount'), max_digits=10, decimal_places=2)
    status = models.CharField(_('status'), max_length=20)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('Service Transaction')
        verbose_name_plural = _('Service Transactions')
        db_table = 'services_transaction'

    def __str__(self):
        return f"{self.user.email} - {self.service_type} - {self.amount}"


class ServiceCategory(models.Model):
    """
    Categories for organizing services.
    """
    name = models.CharField(_('name'), max_length=100, unique=True)
    description = models.TextField(_('description'), blank=True)
    icon = models.CharField(_('icon'), max_length=50, blank=True)  # Font Awesome icon class
    is_active = models.BooleanField(_('active'), default=True)
    display_order = models.PositiveIntegerField(_('display order'), default=0)
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('Service Category')
        verbose_name_plural = _('Service Categories')
        db_table = 'services_category'
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name


class SavedService(models.Model):
    """
    User's saved frequently used services.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_services')
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name='saved_by')
    service_type = models.CharField(_('service type'), max_length=20)
    customer_details = models.JSONField(_('customer details'), default=dict)  # Store customer ID, meter number, etc.
    nickname = models.CharField(_('nickname'), max_length=100, blank=True)
    is_favorite = models.BooleanField(_('favorite'), default=False)
    last_used = models.DateTimeField(_('last used'), null=True, blank=True)
    usage_count = models.PositiveIntegerField(_('usage count'), default=0)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('Saved Service')
        verbose_name_plural = _('Saved Services')
        db_table = 'services_saved'
        unique_together = ['user', 'provider', 'service_type']
        ordering = ['-is_favorite', 'last_used']

    def __str__(self):
        return f"{self.user.email} - {self.provider.name}"