"""
Gift card models for SecureBank.
Handles gift card trading, validation, and management.
"""

import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from decimal import Decimal

User = get_user_model()


class GiftCardType(models.Model):
    """
    Supported gift card types and categories.
    """

    CATEGORY_CHOICES = [
        ("RETAIL", _("Retail")),
        ("GAMING", _("Gaming")),
        ("STREAMING", _("Streaming")),
        ("FOOD", _("Food & Dining")),
        ("TRAVEL", _("Travel")),
        ("GENERAL", _("General Purpose")),
    ]

    name = models.CharField(_("name"), max_length=100, unique=True)
    category = models.CharField(_("category"), max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField(_("description"), blank=True)
    logo = models.ImageField(
        _("logo"), upload_to="giftcard_logos/", null=True, blank=True
    )
    is_active = models.BooleanField(_("active"), default=True)

    # Rates and limits
    buy_rate = models.DecimalField(
        _("buy rate %"), max_digits=5, decimal_places=2, default=Decimal("85.00")
    )  # Percentage of face value
    sell_rate = models.DecimalField(
        _("sell rate %"), max_digits=5, decimal_places=2, default=Decimal("95.00")
    )  # Percentage of face value
    min_amount = models.DecimalField(
        _("minimum amount"), max_digits=10, decimal_places=2, default=Decimal("10.00")
    )
    max_amount = models.DecimalField(
        _("maximum amount"), max_digits=10, decimal_places=2, default=Decimal("1000.00")
    )

    # Supported countries
    supported_countries = models.TextField(
        _("supported countries"),
        help_text="Comma-separated country codes",
        default="US,CA,UK",
    )

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("Gift Card Type")
        verbose_name_plural = _("Gift Card Types")
        db_table = "giftcards_giftcard_type"

    def __str__(self):
        return f"{self.name} ({self.category})"


class GiftCard(models.Model):
    """
    Individual gift card instances.
    """

    CARD_STATUS_CHOICES = [
        ("PENDING", _("Pending Verification")),
        ("VERIFIED", _("Verified")),
        ("REJECTED", _("Rejected")),
        ("SOLD", _("Sold")),
        ("EXPIRED", _("Expired")),
        ("CANCELLED", _("Cancelled")),
    ]

    CONDITION_CHOICES = [
        ("NEW", _("New")),
        ("LIKE_NEW", _("Like New")),
        ("GOOD", _("Good")),
        ("FAIR", _("Fair")),
        ("POOR", _("Poor")),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    seller = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sold_giftcards"
    )
    gift_card_type = models.ForeignKey(
        GiftCardType, on_delete=models.CASCADE, related_name="cards"
    )

    # Card details
    card_code = models.CharField(_("card code"), max_length=100)
    pin = models.CharField(_("PIN"), max_length=50, blank=True)
    face_value = models.DecimalField(_("face value"), max_digits=10, decimal_places=2)
    currency = models.CharField(_("currency"), max_length=3, default="USD")
    expiry_date = models.DateField(_("expiry date"), null=True, blank=True)
    condition = models.CharField(
        _("condition"), max_length=10, choices=CONDITION_CHOICES, default="NEW"
    )

    # Receipt/Proof
    receipt_image = models.ImageField(
        _("receipt image"), upload_to="giftcard_receipts/", null=True, blank=True
    )
    card_image = models.ImageField(
        _("card image"), upload_to="giftcard_images/", null=True, blank=True
    )

    # Status and pricing
    status = models.CharField(
        _("status"), max_length=20, choices=CARD_STATUS_CHOICES, default="PENDING"
    )
    offered_price = models.DecimalField(
        _("offered price"), max_digits=10, decimal_places=2
    )
    final_price = models.DecimalField(
        _("final price"), max_digits=10, decimal_places=2, null=True, blank=True
    )

    # Verification
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_giftcards",
    )
    verification_notes = models.TextField(_("verification notes"), blank=True)
    verified_at = models.DateTimeField(_("verified at"), null=True, blank=True)

    # Additional info
    notes = models.TextField(_("notes"), blank=True)
    country = models.CharField(_("country"), max_length=2, default="US")

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("Gift Card")
        verbose_name_plural = _("Gift Cards")
        db_table = "giftcards_giftcard"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.gift_card_type.name} - ${self.face_value} - {self.status}"

    @property
    def is_verified(self):
        return self.status == "VERIFIED"

    @property
    def is_sold(self):
        return self.status == "SOLD"

    def calculate_offered_price(self):
        """Calculate offered price based on card type rates and condition."""
        base_rate = self.gift_card_type.buy_rate

        # Adjust rate based on condition
        condition_adjustments = {
            "NEW": 1.0,
            "LIKE_NEW": 0.95,
            "GOOD": 0.90,
            "FAIR": 0.80,
            "POOR": 0.70,
        }

        adjusted_rate = base_rate * condition_adjustments.get(self.condition, 0.70)
        self.offered_price = (self.face_value * adjusted_rate) / 100
        return self.offered_price


class GiftCardTransaction(models.Model):
    """
    Gift card buy/sell transactions.
    """

    TRANSACTION_TYPE_CHOICES = [
        ("BUY", _("Buy from User")),
        ("SELL", _("Sell to User")),
        ("TRADE", _("Trade")),
    ]

    STATUS_CHOICES = [
        ("PENDING", _("Pending")),
        ("PROCESSING", _("Processing")),
        ("COMPLETED", _("Completed")),
        ("CANCELLED", _("Cancelled")),
        ("DISPUTED", _("Disputed")),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference = models.CharField(_("transaction reference"), max_length=50, unique=True)
    transaction_type = models.CharField(
        _("transaction type"), max_length=10, choices=TRANSACTION_TYPE_CHOICES
    )

    # Parties involved
    buyer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="bought_giftcards",
        null=True,
        blank=True,
    )
    seller = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sold_giftcard_transactions"
    )
    gift_card = models.ForeignKey(
        GiftCard, on_delete=models.CASCADE, related_name="transactions"
    )

    # Financial details
    amount = models.DecimalField(_("amount"), max_digits=10, decimal_places=2)
    fee = models.DecimalField(
        _("fee"), max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    total_amount = models.DecimalField(
        _("total amount"), max_digits=10, decimal_places=2
    )

    # Status
    status = models.CharField(
        _("status"), max_length=20, choices=STATUS_CHOICES, default="PENDING"
    )

    # Payment details
    payment_method = models.CharField(_("payment method"), max_length=50, blank=True)
    payment_reference = models.CharField(
        _("payment reference"), max_length=100, blank=True
    )

    # Security
    requires_verification = models.BooleanField(
        _("requires verification"), default=True
    )
    verified = models.BooleanField(_("verified"), default=False)

    # Metadata
    ip_address = models.GenericIPAddressField(_("IP address"), null=True, blank=True)
    user_agent = models.TextField(_("user agent"), blank=True)
    notes = models.TextField(_("notes"), blank=True)

    # Timestamps
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    processed_at = models.DateTimeField(_("processed at"), null=True, blank=True)
    completed_at = models.DateTimeField(_("completed at"), null=True, blank=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("Gift Card Transaction")
        verbose_name_plural = _("Gift Card Transactions")
        db_table = "giftcards_transaction"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.reference} - {self.transaction_type} - ${self.amount}"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = self.generate_reference()

        # Calculate total amount
        self.total_amount = self.amount + self.fee

        super().save(*args, **kwargs)

    def generate_reference(self):
        """Generate unique transaction reference."""
        import random
        import string

        while True:
            prefix = "GFT"
            timestamp = (
                str(int(self.created_at.timestamp() * 1000))
                if self.created_at
                else str(int(uuid.uuid4().int)[:10])
            )
            random_str = "".join(
                random.choices(string.ascii_uppercase + string.digits, k=8)
            )
            reference = f"{prefix}{timestamp}{random_str}"

            if not GiftCardTransaction.objects.filter(reference=reference).exists():
                return reference


class GiftCardRate(models.Model):
    """
    Dynamic gift card rates based on market conditions.
    """

    gift_card_type = models.ForeignKey(
        GiftCardType, on_delete=models.CASCADE, related_name="rates"
    )
    buy_rate = models.DecimalField(_("buy rate %"), max_digits=5, decimal_places=2)
    sell_rate = models.DecimalField(_("sell rate %"), max_digits=5, decimal_places=2)
    min_amount = models.DecimalField(
        _("minimum amount"), max_digits=10, decimal_places=2
    )
    max_amount = models.DecimalField(
        _("maximum amount"), max_digits=10, decimal_places=2
    )

    # Rate validity
    valid_from = models.DateTimeField(_("valid from"), auto_now_add=True)
    valid_until = models.DateTimeField(_("valid until"), null=True, blank=True)
    is_active = models.BooleanField(_("active"), default=True)

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)

    class Meta:
        verbose_name = _("Gift Card Rate")
        verbose_name_plural = _("Gift Card Rates")
        db_table = "giftcards_rate"
        ordering = ["-valid_from"]

    def __str__(self):
        return f"{self.gift_card_type.name} - Buy: {self.buy_rate}%, Sell: {self.sell_rate}%"


class GiftCardDispute(models.Model):
    """
    Dispute resolution for gift card transactions.
    """

    DISPUTE_STATUS_CHOICES = [
        ("OPEN", _("Open")),
        ("UNDER_REVIEW", _("Under Review")),
        ("RESOLVED", _("Resolved")),
        ("CLOSED", _("Closed")),
    ]

    DISPUTE_TYPE_CHOICES = [
        ("INVALID_CODE", _("Invalid Code")),
        ("USED_CODE", _("Already Used")),
        ("WRONG_VALUE", _("Wrong Value")),
        ("EXPIRED", _("Expired Card")),
        ("OTHER", _("Other")),
    ]

    transaction = models.OneToOneField(
        GiftCardTransaction, on_delete=models.CASCADE, related_name="dispute"
    )
    raised_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="raised_disputes"
    )
    dispute_type = models.CharField(
        _("dispute type"), max_length=20, choices=DISPUTE_TYPE_CHOICES
    )
    description = models.TextField(_("description"))
    evidence = models.ImageField(
        _("evidence"), upload_to="dispute_evidence/", null=True, blank=True
    )

    status = models.CharField(
        _("status"), max_length=20, choices=DISPUTE_STATUS_CHOICES, default="OPEN"
    )
    resolution = models.TextField(_("resolution"), blank=True)
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resolved_disputes",
    )
    resolved_at = models.DateTimeField(_("resolved at"), null=True, blank=True)

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("Gift Card Dispute")
        verbose_name_plural = _("Gift Card Disputes")
        db_table = "giftcards_dispute"

    def __str__(self):
        return f"Dispute for {self.transaction.reference} - {self.status}"


class GiftCardInventory(models.Model):
    """
    Available gift cards for sale to users.
    """

    gift_card_type = models.ForeignKey(
        GiftCardType, on_delete=models.CASCADE, related_name="inventory"
    )
    quantity = models.PositiveIntegerField(_("quantity"), default=0)
    face_value = models.DecimalField(_("face value"), max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(
        _("selling price"), max_digits=10, decimal_places=2
    )
    is_available = models.BooleanField(_("available"), default=True)

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("Gift Card Inventory")
        verbose_name_plural = _("Gift Card Inventory")
        db_table = "giftcards_inventory"
        unique_together = ["gift_card_type", "face_value"]

    def __str__(self):
        return (
            f"{self.gift_card_type.name} ${self.face_value} - {self.quantity} available"
        )
