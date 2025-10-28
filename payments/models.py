"""
Payment models for SecureBank.
Handles Paystack integration and payment processing.
"""

import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from decimal import Decimal

from accounts.models import BankAccount

User = get_user_model()


class PaymentMethod(models.Model):
    """
    User's saved payment methods.
    """

    METHOD_TYPE_CHOICES = [
        ("CARD", _("Debit/Credit Card")),
        ("BANK_TRANSFER", _("Bank Transfer")),
        ("USSD", _("USSD")),
        ("QR", _("QR Code")),
        ("MOBILE_MONEY", _("Mobile Money")),
    ]

    STATUS_CHOICES = [
        ("ACTIVE", _("Active")),
        ("INACTIVE", _("Inactive")),
        ("EXPIRED", _("Expired")),
        ("BLOCKED", _("Blocked")),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="payment_methods"
    )
    method_type = models.CharField(
        _("method type"), max_length=20, choices=METHOD_TYPE_CHOICES
    )

    # Card details (encrypted)
    card_last4 = models.CharField(_("card last 4"), max_length=4, blank=True)
    card_brand = models.CharField(_("card brand"), max_length=50, blank=True)
    card_expiry_month = models.CharField(
        _("card expiry month"), max_length=2, blank=True
    )
    card_expiry_year = models.CharField(_("card expiry year"), max_length=4, blank=True)
    card_signature = models.TextField(
        _("card signature"), blank=True
    )  # Paystack signature

    # Bank details
    bank_name = models.CharField(_("bank name"), max_length=100, blank=True)
    account_number = models.CharField(_("account number"), max_length=50, blank=True)
    account_name = models.CharField(_("account name"), max_length=200, blank=True)

    # General
    nickname = models.CharField(_("nickname"), max_length=100, blank=True)
    is_default = models.BooleanField(_("default method"), default=False)
    status = models.CharField(
        _("status"), max_length=20, choices=STATUS_CHOICES, default="ACTIVE"
    )

    # Paystack integration
    paystack_authorization_code = models.CharField(
        _("Paystack authorization code"), max_length=200, blank=True
    )
    paystack_customer_code = models.CharField(
        _("Paystack customer code"), max_length=200, blank=True
    )
    paystack_email = models.EmailField(_("Paystack email"), blank=True)

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("Payment Method")
        verbose_name_plural = _("Payment Methods")
        db_table = "payments_payment_method"
        ordering = ["-is_default", "-created_at"]

    def __str__(self):
        return f"{self.user.email} - {self.method_type} - {self.nickname or self.get_display_name()}"

    def get_display_name(self):
        """Get display name for payment method."""
        if self.method_type == "CARD" and self.card_last4:
            return f"{self.card_brand} ****{self.card_last4}"
        elif self.method_type == "BANK_TRANSFER" and self.account_number:
            return f"{self.bank_name} ****{self.account_number[-4:]}"
        else:
            return self.method_type


class PaymentTransaction(models.Model):
    """
    Payment transactions using various payment methods.
    """

    TRANSACTION_TYPE_CHOICES = [
        ("DEPOSIT", _("Deposit")),
        ("WITHDRAWAL", _("Withdrawal")),
        ("TRANSFER", _("Transfer")),
        ("SERVICE_PAYMENT", _("Service Payment")),
        ("CRYPTO_PURCHASE", _("Crypto Purchase")),
        ("GIFTCARD_PURCHASE", _("Gift Card Purchase")),
    ]

    STATUS_CHOICES = [
        ("INITIATED", _("Initiated")),
        ("PENDING", _("Pending")),
        ("PROCESSING", _("Processing")),
        ("SUCCESS", _("Success")),
        ("FAILED", _("Failed")),
        ("CANCELLED", _("Cancelled")),
        ("REFUNDED", _("Refunded")),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference = models.CharField(_("transaction reference"), max_length=50, unique=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="payment_transactions"
    )
    payment_method = models.ForeignKey(
        PaymentMethod,
        on_delete=models.CASCADE,
        related_name="transactions",
        null=True,
        blank=True,
    )
    account = models.ForeignKey(
        BankAccount,
        on_delete=models.CASCADE,
        related_name="payment_transactions",
        null=True,
        blank=True,
    )

    # Transaction details
    transaction_type = models.CharField(
        _("transaction type"), max_length=20, choices=TRANSACTION_TYPE_CHOICES
    )
    amount = models.DecimalField(
        _("amount"),
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    currency = models.CharField(_("currency"), max_length=3, default="NGN")
    description = models.TextField(_("description"), blank=True)

    # Fees
    processing_fee = models.DecimalField(
        _("processing fee"), max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    service_fee = models.DecimalField(
        _("service fee"), max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    total_amount = models.DecimalField(
        _("total amount"), max_digits=15, decimal_places=2
    )

    # Status
    status = models.CharField(
        _("status"), max_length=20, choices=STATUS_CHOICES, default="INITIATED"
    )

    # Paystack integration
    paystack_reference = models.CharField(
        _("Paystack reference"), max_length=100, blank=True
    )
    paystack_access_code = models.CharField(
        _("Paystack access code"), max_length=200, blank=True
    )
    paystack_payment_url = models.URLField(_("Paystack payment URL"), blank=True)

    # Metadata
    ip_address = models.GenericIPAddressField(_("IP address"), null=True, blank=True)
    user_agent = models.TextField(_("user agent"), blank=True)
    metadata = models.JSONField(_("metadata"), default=dict, blank=True)

    # Timestamps
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    paid_at = models.DateTimeField(_("paid at"), null=True, blank=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("Payment Transaction")
        verbose_name_plural = _("Payment Transactions")
        db_table = "payments_payment_transaction"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["reference"]),
            models.Index(fields=["status"]),
            models.Index(fields=["paystack_reference"]),
            models.Index(fields=["user"]),
        ]

    def __str__(self):
        return f"{self.reference} - {self.transaction_type} - {self.amount} {self.currency}"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = self.generate_reference()

        # Calculate total amount
        self.total_amount = self.amount + self.processing_fee + self.service_fee

        super().save(*args, **kwargs)

    def generate_reference(self):
        """Generate unique transaction reference."""
        import random
        import string

        while True:
            prefix = "PAY"
            timestamp = (
                str(int(self.created_at.timestamp() * 1000))
                if self.created_at
                else str(int(uuid.uuid4().int)[:10])
            )
            random_str = "".join(
                random.choices(string.ascii_uppercase + string.digits, k=8)
            )
            reference = f"{prefix}{timestamp}{random_str}"

            if not PaymentTransaction.objects.filter(reference=reference).exists():
                return reference

    @property
    def is_successful(self):
        return self.status == "SUCCESS"

    @property
    def is_pending(self):
        return self.status in ["INITIATED", "PENDING", "PROCESSING"]


class PaystackCustomer(models.Model):
    """
    Paystack customer information.
    """

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="paystack_customer"
    )
    customer_code = models.CharField(_("customer code"), max_length=200, unique=True)
    customer_email = models.EmailField(_("customer email"))
    first_name = models.CharField(_("first name"), max_length=100)
    last_name = models.CharField(_("last name"), max_length=100)
    phone = models.CharField(_("phone"), max_length=20, blank=True)
    metadata = models.JSONField(_("metadata"), default=dict, blank=True)

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("Paystack Customer")
        verbose_name_plural = _("Paystack Customers")
        db_table = "payments_paystack_customer"

    def __str__(self):
        return f"{self.user.email} - {self.customer_code}"


class PaystackWebhook(models.Model):
    """
    Paystack webhook events.
    """

    EVENT_TYPE_CHOICES = [
        ("charge.success", _("Charge Success")),
        ("charge.failed", _("Charge Failed")),
        ("transfer.success", _("Transfer Success")),
        ("transfer.failed", _("Transfer Failed")),
        ("transfer.reversed", _("Transfer Reversed")),
        ("customeridentification.failed", _("Customer Identification Failed")),
        ("subscription.create", _("Subscription Create")),
        ("subscription.not_renew", _("Subscription Not Renew")),
        ("invoice.create", _("Invoice Create")),
        ("invoice.payment_failed", _("Invoice Payment Failed")),
        ("invoice.update", _("Invoice Update")),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_type = models.CharField(
        _("event type"), max_length=50, choices=EVENT_TYPE_CHOICES
    )
    reference = models.CharField(_("reference"), max_length=100)
    data = models.JSONField(_("event data"))
    processed = models.BooleanField(_("processed"), default=False)
    processing_attempts = models.PositiveIntegerField(
        _("processing attempts"), default=0
    )
    error_message = models.TextField(_("error message"), blank=True)

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    processed_at = models.DateTimeField(_("processed at"), null=True, blank=True)

    class Meta:
        verbose_name = _("Paystack Webhook")
        verbose_name_plural = _("Paystack Webhooks")
        db_table = "payments_paystack_webhook"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["event_type"]),
            models.Index(fields=["reference"]),
            models.Index(fields=["processed"]),
        ]

    def __str__(self):
        return f"{self.event_type} - {self.reference}"


class Refund(models.Model):
    """
    Refund transactions.
    """

    STATUS_CHOICES = [
        ("PENDING", _("Pending")),
        ("PROCESSING", _("Processing")),
        ("COMPLETED", _("Completed")),
        ("FAILED", _("Failed")),
        ("CANCELLED", _("Cancelled")),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference = models.CharField(_("refund reference"), max_length=50, unique=True)
    original_transaction = models.ForeignKey(
        PaymentTransaction, on_delete=models.CASCADE, related_name="refunds"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="refunds")

    # Refund details
    amount = models.DecimalField(_("amount"), max_digits=15, decimal_places=2)
    reason = models.TextField(_("reason"))
    status = models.CharField(
        _("status"), max_length=20, choices=STATUS_CHOICES, default="PENDING"
    )

    # Paystack integration
    paystack_refund_reference = models.CharField(
        _("Paystack refund reference"), max_length=100, blank=True
    )

    # Metadata
    processed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="processed_refunds",
    )
    notes = models.TextField(_("notes"), blank=True)

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    processed_at = models.DateTimeField(_("processed at"), null=True, blank=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("Refund")
        verbose_name_plural = _("Refunds")
        db_table = "payments_refund"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.reference} - {self.amount} - {self.status}"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = self.generate_reference()
        super().save(*args, **kwargs)

    def generate_reference(self):
        """Generate unique refund reference."""
        import random
        import string

        while True:
            prefix = "REF"
            timestamp = (
                str(int(self.created_at.timestamp() * 1000))
                if self.created_at
                else str(int(uuid.uuid4().int)[:10])
            )
            random_str = "".join(
                random.choices(string.ascii_uppercase + string.digits, k=8)
            )
            reference = f"{prefix}{timestamp}{random_str}"

            if not Refund.objects.filter(reference=reference).exists():
                return reference


class PaymentNotification(models.Model):
    """
    Payment notifications to users.
    """

    NOTIFICATION_TYPE_CHOICES = [
        ("PAYMENT_SUCCESS", _("Payment Success")),
        ("PAYMENT_FAILED", _("Payment Failed")),
        ("REFUND_PROCESSED", _("Refund Processed")),
        ("PAYMENT_METHOD_EXPIRED", _("Payment Method Expired")),
        ("PAYMENT_METHOD_ADDED", _("Payment Method Added")),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="payment_notifications"
    )
    notification_type = models.CharField(
        _("notification type"), max_length=30, choices=NOTIFICATION_TYPE_CHOICES
    )
    title = models.CharField(_("title"), max_length=200)
    message = models.TextField(_("message"))
    transaction = models.ForeignKey(
        PaymentTransaction,
        on_delete=models.CASCADE,
        related_name="notifications",
        null=True,
        blank=True,
    )

    is_read = models.BooleanField(_("read"), default=False)
    email_sent = models.BooleanField(_("email sent"), default=False)
    sms_sent = models.BooleanField(_("SMS sent"), default=False)

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    read_at = models.DateTimeField(_("read at"), null=True, blank=True)

    class Meta:
        verbose_name = _("Payment Notification")
        verbose_name_plural = _("Payment Notifications")
        db_table = "payments_notification"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email} - {self.notification_type}"
