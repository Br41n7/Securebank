"""
Transaction models for SecureBank.
Handles all types of financial transactions with proper security and auditing.
"""

import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum
from decimal import Decimal

from accounts.models import BankAccount

User = get_user_model()


class Transaction(models.Model):
    """
    Main transaction model for all financial operations.
    """

    TRANSACTION_TYPE_CHOICES = [
        ("TRANSFER", _("Bank Transfer")),
        ("DEPOSIT", _("Deposit")),
        ("WITHDRAWAL", _("Withdrawal")),
        ("PAYMENT", _("Bill Payment")),
        ("AIRTIME", _("Airtime Top-up")),
        ("CRYPTO_BUY", _("Crypto Purchase")),
        ("CRYPTO_SELL", _("Crypto Sale")),
        ("GIFTCARD_BUY", _("Gift Card Purchase")),
        ("GIFTCARD_SELL", _("Gift Card Sale")),
        ("SCHOOL_FEE", _("School Fee Payment")),
        ("ELECTRIC_BILL", _("Electric Bill Payment")),
        ("REFUND", _("Refund")),
        ("CHARGE", _("Service Charge")),
    ]

    STATUS_CHOICES = [
        ("PENDING", _("Pending")),
        ("PROCESSING", _("Processing")),
        ("COMPLETED", _("Completed")),
        ("FAILED", _("Failed")),
        ("CANCELLED", _("Cancelled")),
        ("REVERSED", _("Reversed")),
    ]

    PRIORITY_CHOICES = [
        ("LOW", _("Low")),
        ("NORMAL", _("Normal")),
        ("HIGH", _("High")),
        ("URGENT", _("Urgent")),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference = models.CharField(_("transaction reference"), max_length=50, unique=True)
    transaction_type = models.CharField(
        _("transaction type"), max_length=20, choices=TRANSACTION_TYPE_CHOICES
    )

    # Source and Destination
    source_account = models.ForeignKey(
        BankAccount,
        on_delete=models.CASCADE,
        related_name="outgoing_transactions",
        null=True,
        blank=True,
    )
    destination_account = models.ForeignKey(
        BankAccount,
        on_delete=models.CASCADE,
        related_name="incoming_transactions",
        null=True,
        blank=True,
    )

    # Transaction Details
    amount = models.DecimalField(
        _("amount"),
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    currency = models.CharField(_("currency"), max_length=3, default="NGN")
    description = models.TextField(_("description"), blank=True)
    narration = models.TextField(_("narration"), blank=True)

    # External transaction details
    recipient_name = models.CharField(_("recipient name"), max_length=200, blank=True)
    recipient_account = models.CharField(
        _("recipient account"), max_length=50, blank=True
    )
    recipient_bank = models.CharField(_("recipient bank"), max_length=200, blank=True)

    # Status and Processing
    status = models.CharField(
        _("status"), max_length=20, choices=STATUS_CHOICES, default="PENDING"
    )
    priority = models.CharField(
        _("priority"), max_length=10, choices=PRIORITY_CHOICES, default="NORMAL"
    )

    # Fees and Charges
    fee = models.DecimalField(
        _("fee"), max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    tax = models.DecimalField(
        _("tax"), max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    total_amount = models.DecimalField(
        _("total amount"), max_digits=15, decimal_places=2
    )

    # Security and Verification
    requires_otp = models.BooleanField(_("requires OTP"), default=False)
    otp_verified = models.BooleanField(_("OTP verified"), default=False)
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_transactions",
    )

    # Metadata
    ip_address = models.GenericIPAddressField(_("IP address"), null=True, blank=True)
    user_agent = models.TextField(_("user agent"), blank=True)
    device_id = models.CharField(_("device ID"), max_length=100, blank=True)

    # Timestamps
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    processed_at = models.DateTimeField(_("processed at"), null=True, blank=True)
    completed_at = models.DateTimeField(_("completed at"), null=True, blank=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("Transaction")
        verbose_name_plural = _("Transactions")
        db_table = "transactions_transaction"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["reference"]),
            models.Index(fields=["status"]),
            models.Index(fields=["transaction_type"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["source_account"]),
            models.Index(fields=["destination_account"]),
        ]

    def __str__(self):
        return f"{self.reference} - {self.transaction_type} - {self.amount} {self.currency}"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = self.generate_reference()

        # Calculate total amount
        self.total_amount = self.amount + self.fee + self.tax

        super().save(*args, **kwargs)

    def generate_reference(self):
        """Generate unique transaction reference."""
        import random
        import string

        while True:
            prefix = "TXN"
            timestamp = (
                str(int(self.created_at.timestamp() * 1000))
                if self.created_at
                else str(int(uuid.uuid4().int)[:10])
            )
            random_str = "".join(
                random.choices(string.ascii_uppercase + string.digits, k=8)
            )
            reference = f"{prefix}{timestamp}{random_str}"

            if not Transaction.objects.filter(reference=reference).exists():
                return reference

    @property
    def is_completed(self):
        return self.status == "COMPLETED"

    @property
    def is_pending(self):
        return self.status == "PENDING"

    @property
    def is_failed(self):
        return self.status == "FAILED"

    def can_be_cancelled(self):
        """Check if transaction can be cancelled."""
        return self.status in ["PENDING", "PROCESSING"]

    def can_be_reversed(self):
        """Check if transaction can be reversed."""
        return self.status == "COMPLETED"


class TransactionLog(models.Model):
    """
    Audit log for all transaction changes.
    """

    ACTION_CHOICES = [
        ("CREATED", _("Created")),
        ("UPDATED", _("Updated")),
        ("CANCELLED", _("Cancelled")),
        ("COMPLETED", _("Completed")),
        ("FAILED", _("Failed")),
        ("REVERSED", _("Reversed")),
        ("OTP_REQUESTED", _("OTP Requested")),
        ("OTP_VERIFIED", _("OTP Verified")),
    ]

    transaction = models.ForeignKey(
        Transaction, on_delete=models.CASCADE, related_name="logs"
    )
    action = models.CharField(_("action"), max_length=20, choices=ACTION_CHOICES)
    old_status = models.CharField(_("old status"), max_length=20, blank=True)
    new_status = models.CharField(_("new status"), max_length=20, blank=True)
    details = models.TextField(_("details"), blank=True)
    ip_address = models.GenericIPAddressField(_("IP address"), null=True, blank=True)
    user_agent = models.TextField(_("user agent"), blank=True)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)

    class Meta:
        verbose_name = _("Transaction Log")
        verbose_name_plural = _("Transaction Logs")
        db_table = "transactions_transaction_log"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.transaction.reference} - {self.action}"


class Beneficiary(models.Model):
    """
    Saved beneficiaries for quick transfers.
    """

    BENEFICIARY_TYPE_CHOICES = [
        ("INTERNAL", _("Internal Transfer")),
        ("EXTERNAL", _("External Transfer")),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="beneficiaries"
    )
    name = models.CharField(_("beneficiary name"), max_length=200)
    account_number = models.CharField(_("account number"), max_length=50)
    bank_name = models.CharField(_("bank name"), max_length=200)
    beneficiary_type = models.CharField(
        _("beneficiary type"), max_length=10, choices=BENEFICIARY_TYPE_CHOICES
    )
    nickname = models.CharField(_("nickname"), max_length=100, blank=True)
    is_favorite = models.BooleanField(_("favorite"), default=False)
    last_used = models.DateTimeField(_("last used"), null=True, blank=True)
    usage_count = models.PositiveIntegerField(_("usage count"), default=0)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("Beneficiary")
        verbose_name_plural = _("Beneficiaries")
        db_table = "transactions_beneficiary"
        unique_together = ["user", "account_number", "bank_name"]
        ordering = ["-is_favorite", "name"]

    def __str__(self):
        return f"{self.name} - {self.account_number}"


class TransactionLimit(models.Model):
    """
    Transaction limits for different user tiers and transaction types.
    """

    TIER_CHOICES = [
        ("BASIC", _("Basic")),
        ("STANDARD", _("Standard")),
        ("PREMIUM", _("Premium")),
        ("BUSINESS", _("Business")),
    ]

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="transaction_limits"
    )
    tier = models.CharField(
        _("tier"), max_length=10, choices=TIER_CHOICES, default="BASIC"
    )

    # Daily limits
    daily_transfer_limit = models.DecimalField(
        _("daily transfer limit"),
        max_digits=15,
        decimal_places=2,
        default=Decimal("100000.00"),
    )
    daily_withdrawal_limit = models.DecimalField(
        _("daily withdrawal limit"),
        max_digits=15,
        decimal_places=2,
        default=Decimal("50000.00"),
    )
    daily_crypto_limit = models.DecimalField(
        _("daily crypto limit"),
        max_digits=15,
        decimal_places=2,
        default=Decimal("200000.00"),
    )

    # Single transaction limits
    single_transfer_limit = models.DecimalField(
        _("single transfer limit"),
        max_digits=15,
        decimal_places=2,
        default=Decimal("50000.00"),
    )
    single_withdrawal_limit = models.DecimalField(
        _("single withdrawal limit"),
        max_digits=15,
        decimal_places=2,
        default=Decimal("20000.00"),
    )
    single_crypto_limit = models.DecimalField(
        _("single crypto limit"),
        max_digits=15,
        decimal_places=2,
        default=Decimal("100000.00"),
    )

    # Monthly limits
    monthly_transfer_limit = models.DecimalField(
        _("monthly transfer limit"),
        max_digits=15,
        decimal_places=2,
        default=Decimal("2000000.00"),
    )
    monthly_withdrawal_limit = models.DecimalField(
        _("monthly withdrawal limit"),
        max_digits=15,
        decimal_places=2,
        default=Decimal("1000000.00"),
    )

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("Transaction Limit")
        verbose_name_plural = _("Transaction Limits")
        db_table = "transactions_transaction_limit"

    def __str__(self):
        return f"{self.user.email} - {self.tier} Limits"

    def check_daily_limit(self, transaction_type, amount):
        """Check if amount exceeds daily limit for transaction type."""
        from django.utils import timezone
        from django.db.models import Sum

        today = timezone.now().date()

        if transaction_type in ["TRANSFER", "PAYMENT"]:
            daily_total = Transaction.objects.filter(
                source_account__user=self.user,
                transaction_type__in=["TRANSFER", "PAYMENT"],
                status="COMPLETED",
                created_at__date=today,
            ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

            return daily_total + amount <= self.daily_transfer_limit

        elif transaction_type == "WITHDRAWAL":
            daily_total = Transaction.objects.filter(
                source_account__user=self.user,
                transaction_type="WITHDRAWAL",
                status="COMPLETED",
                created_at__date=today,
            ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

            return daily_total + amount <= self.daily_withdrawal_limit

        elif transaction_type in ["CRYPTO_BUY", "CRYPTO_SELL"]:
            daily_total = Transaction.objects.filter(
                source_account__user=self.user,
                transaction_type__in=["CRYPTO_BUY", "CRYPTO_SELL"],
                status="COMPLETED",
                created_at__date=today,
            ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

            return daily_total + amount <= self.daily_crypto_limit

        return True


class ScheduledTransaction(models.Model):
    """
    Scheduled/recurring transactions.
    """

    FREQUENCY_CHOICES = [
        ("DAILY", _("Daily")),
        ("WEEKLY", _("Weekly")),
        ("MONTHLY", _("Monthly")),
        ("YEARLY", _("Yearly")),
        ("CUSTOM", _("Custom")),
    ]

    STATUS_CHOICES = [
        ("ACTIVE", _("Active")),
        ("PAUSED", _("Paused")),
        ("COMPLETED", _("Completed")),
        ("CANCELLED", _("Cancelled")),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="scheduled_transactions"
    )
    source_account = models.ForeignKey(
        BankAccount, on_delete=models.CASCADE, related_name="scheduled_outgoing"
    )
    beneficiary_name = models.CharField(_("beneficiary name"), max_length=200)
    beneficiary_account = models.CharField(_("beneficiary account"), max_length=50)
    beneficiary_bank = models.CharField(_("beneficiary bank"), max_length=200)
    amount = models.DecimalField(_("amount"), max_digits=15, decimal_places=2)
    description = models.TextField(_("description"), blank=True)
    frequency = models.CharField(
        _("frequency"), max_length=10, choices=FREQUENCY_CHOICES
    )
    start_date = models.DateField(_("start date"))
    end_date = models.DateField(_("end date"), null=True, blank=True)
    next_execution = models.DateTimeField(_("next execution"))
    execution_count = models.PositiveIntegerField(_("execution count"), default=0)
    max_executions = models.PositiveIntegerField(
        _("max executions"), null=True, blank=True
    )
    status = models.CharField(
        _("status"), max_length=10, choices=STATUS_CHOICES, default="ACTIVE"
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("Scheduled Transaction")
        verbose_name_plural = _("Scheduled Transactions")
        db_table = "transactions_scheduled_transaction"
        ordering = ["next_execution"]

    def __str__(self):
        return f"{self.user.email} - {self.beneficiary_name} - {self.amount}"
