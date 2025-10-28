"""
Cryptocurrency models for SecureBank.
Handles crypto wallets, transactions, and portfolio management.
"""

import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from decimal import Decimal

from accounts.models import BankAccount

User = get_user_model()


class Cryptocurrency(models.Model):
    """
    Supported cryptocurrencies with their properties.
    """

    CRYPTO_TYPE_CHOICES = [
        ("BTC", _("Bitcoin")),
        ("ETH", _("Ethereum")),
        ("USDT", _("Tether")),
        ("USDC", _("USD Coin")),
        ("BNB", _("Binance Coin")),
        ("ADA", _("Cardano")),
        ("SOL", _("Solana")),
        ("DOT", _("Polkadot")),
    ]

    symbol = models.CharField(_("symbol"), max_length=10, primary_key=True)
    name = models.CharField(_("name"), max_length=50)
    crypto_type = models.CharField(
        _("crypto type"), max_length=10, choices=CRYPTO_TYPE_CHOICES
    )
    current_price = models.DecimalField(
        _("current price"),
        max_digits=20,
        decimal_places=8,
        default=Decimal("0.00000000"),
    )
    market_cap = models.DecimalField(
        _("market cap"), max_digits=20, decimal_places=2, default=Decimal("0.00")
    )
    circulating_supply = models.DecimalField(
        _("circulating supply"),
        max_digits=30,
        decimal_places=8,
        default=Decimal("0.00000000"),
    )
    is_active = models.BooleanField(_("active"), default=True)
    min_purchase_amount = models.DecimalField(
        _("min purchase amount"),
        max_digits=15,
        decimal_places=8,
        default=Decimal("0.00000001"),
    )
    max_purchase_amount = models.DecimalField(
        _("max purchase amount"),
        max_digits=15,
        decimal_places=8,
        default=Decimal("1000000.00000000"),
    )

    # Network fees
    network_fee = models.DecimalField(
        _("network fee"), max_digits=15, decimal_places=8, default=Decimal("0.00000000")
    )
    withdrawal_fee = models.DecimalField(
        _("withdrawal fee"),
        max_digits=15,
        decimal_places=8,
        default=Decimal("0.00000000"),
    )

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("Cryptocurrency")
        verbose_name_plural = _("Cryptocurrencies")
        db_table = "crypto_cryptocurrency"

    def __str__(self):
        return f"{self.name} ({self.symbol})"


class CryptoWallet(models.Model):
    """
    User's cryptocurrency wallets.
    """

    WALLET_TYPE_CHOICES = [
        ("HOT", _("Hot Wallet")),
        ("COLD", _("Cold Wallet")),
        ("CUSTODIAL", _("Custodial Wallet")),
    ]

    STATUS_CHOICES = [
        ("ACTIVE", _("Active")),
        ("FROZEN", _("Frozen")),
        ("CLOSED", _("Closed")),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="crypto_wallets"
    )
    cryptocurrency = models.ForeignKey(
        Cryptocurrency, on_delete=models.CASCADE, related_name="wallets"
    )
    wallet_address = models.CharField(_("wallet address"), max_length=255, unique=True)
    wallet_type = models.CharField(
        _("wallet type"),
        max_length=10,
        choices=WALLET_TYPE_CHOICES,
        default="CUSTODIAL",
    )
    balance = models.DecimalField(
        _("balance"), max_digits=30, decimal_places=8, default=Decimal("0.00000000")
    )
    available_balance = models.DecimalField(
        _("available balance"),
        max_digits=30,
        decimal_places=8,
        default=Decimal("0.00000000"),
    )
    frozen_balance = models.DecimalField(
        _("frozen balance"),
        max_digits=30,
        decimal_places=8,
        default=Decimal("0.00000000"),
    )
    status = models.CharField(
        _("status"), max_length=10, choices=STATUS_CHOICES, default="ACTIVE"
    )
    is_default = models.BooleanField(_("default wallet"), default=False)

    # Security
    private_key_encrypted = models.TextField(_("encrypted private key"), blank=True)
    public_key = models.TextField(_("public key"), blank=True)
    mnemonic_encrypted = models.TextField(_("encrypted mnemonic"), blank=True)

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("Crypto Wallet")
        verbose_name_plural = _("Crypto Wallets")
        db_table = "crypto_wallet"
        unique_together = ["user", "cryptocurrency"]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email} - {self.cryptocurrency.symbol} Wallet"

    @property
    def is_active(self):
        return self.status == "ACTIVE"

    def can_withdraw(self, amount):
        """Check if user can withdraw specified amount."""
        return self.is_active and amount <= self.available_balance


class CryptoTransaction(models.Model):
    """
    Cryptocurrency transactions.
    """

    TRANSACTION_TYPE_CHOICES = [
        ("BUY", _("Buy")),
        ("SELL", _("Sell")),
        ("SEND", _("Send")),
        ("RECEIVE", _("Receive")),
        ("SWAP", _("Swap")),
        ("CONVERT", _("Convert")),
    ]

    STATUS_CHOICES = [
        ("PENDING", _("Pending")),
        ("PROCESSING", _("Processing")),
        ("COMPLETED", _("Completed")),
        ("FAILED", _("Failed")),
        ("CANCELLED", _("Cancelled")),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference = models.CharField(_("transaction reference"), max_length=50, unique=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="crypto_transactions"
    )
    cryptocurrency = models.ForeignKey(
        Cryptocurrency, on_delete=models.CASCADE, related_name="transactions"
    )
    wallet = models.ForeignKey(
        CryptoWallet, on_delete=models.CASCADE, related_name="transactions"
    )
    transaction_type = models.CharField(
        _("transaction type"), max_length=10, choices=TRANSACTION_TYPE_CHOICES
    )

    # Transaction details
    amount = models.DecimalField(
        _("amount"),
        max_digits=30,
        decimal_places=8,
        validators=[MinValueValidator(Decimal("0.00000001"))],
    )
    price_per_unit = models.DecimalField(
        _("price per unit"),
        max_digits=20,
        decimal_places=8,
        default=Decimal("0.00000000"),
    )
    total_value = models.DecimalField(
        _("total value"), max_digits=15, decimal_places=2, default=Decimal("0.00")
    )

    # External transaction details
    to_address = models.CharField(_("to address"), max_length=255, blank=True)
    from_address = models.CharField(_("from address"), max_length=255, blank=True)
    blockchain_tx_hash = models.CharField(
        _("blockchain transaction hash"), max_length=255, blank=True
    )
    confirmations = models.PositiveIntegerField(_("confirmations"), default=0)
    required_confirmations = models.PositiveIntegerField(
        _("required confirmations"), default=3
    )

    # Fees
    network_fee = models.DecimalField(
        _("network fee"), max_digits=15, decimal_places=8, default=Decimal("0.00000000")
    )
    service_fee = models.DecimalField(
        _("service fee"), max_digits=15, decimal_places=2, default=Decimal("0.00")
    )

    # Status
    status = models.CharField(
        _("status"), max_length=20, choices=STATUS_CHOICES, default="PENDING"
    )

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
        verbose_name = _("Crypto Transaction")
        verbose_name_plural = _("Crypto Transactions")
        db_table = "crypto_transaction"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["reference"]),
            models.Index(fields=["status"]),
            models.Index(fields=["transaction_type"]),
            models.Index(fields=["user"]),
            models.Index(fields=["cryptocurrency"]),
        ]

    def __str__(self):
        return f"{self.reference} - {self.transaction_type} {self.amount} {self.cryptocurrency.symbol}"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = self.generate_reference()

        # Calculate total value
        if self.amount and self.price_per_unit:
            self.total_value = self.amount * self.price_per_unit

        super().save(*args, **kwargs)

    def generate_reference(self):
        """Generate unique transaction reference."""
        import random
        import string

        while True:
            prefix = "CRX"
            timestamp = (
                str(int(self.created_at.timestamp() * 1000))
                if self.created_at
                else str(int(uuid.uuid4().int)[:10])
            )
            random_str = "".join(
                random.choices(string.ascii_uppercase + string.digits, k=8)
            )
            reference = f"{prefix}{timestamp}{random_str}"

            if not CryptoTransaction.objects.filter(reference=reference).exists():
                return reference

    @property
    def is_completed(self):
        return self.status == "COMPLETED"

    @property
    def is_pending(self):
        return self.status == "PENDING"

    def can_be_cancelled(self):
        """Check if transaction can be cancelled."""
        return self.status in ["PENDING", "PROCESSING"]


class CryptoPriceHistory(models.Model):
    """
    Historical price data for cryptocurrencies.
    """

    cryptocurrency = models.ForeignKey(
        Cryptocurrency, on_delete=models.CASCADE, related_name="price_history"
    )
    price = models.DecimalField(_("price"), max_digits=20, decimal_places=8)
    market_cap = models.DecimalField(
        _("market cap"), max_digits=20, decimal_places=2, default=Decimal("0.00")
    )
    volume_24h = models.DecimalField(
        _("24h volume"), max_digits=20, decimal_places=2, default=Decimal("0.00")
    )
    timestamp = models.DateTimeField(_("timestamp"), auto_now_add=True)

    class Meta:
        verbose_name = _("Crypto Price History")
        verbose_name_plural = _("Crypto Price History")
        db_table = "crypto_price_history"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["cryptocurrency", "timestamp"]),
        ]

    def __str__(self):
        return f"{self.cryptocurrency.symbol} - {self.price} at {self.timestamp}"


class CryptoPortfolio(models.Model):
    """
    User's crypto portfolio summary.
    """

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="crypto_portfolio"
    )
    total_value_usd = models.DecimalField(
        _("total value USD"), max_digits=15, decimal_places=2, default=Decimal("0.00")
    )
    total_invested_usd = models.DecimalField(
        _("total invested USD"),
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    total_profit_loss_usd = models.DecimalField(
        _("total profit/loss USD"),
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    total_profit_loss_percentage = models.DecimalField(
        _("total profit/loss %"),
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    # Auto-updated fields
    last_updated = models.DateTimeField(_("last updated"), auto_now=True)

    class Meta:
        verbose_name = _("Crypto Portfolio")
        verbose_name_plural = _("Crypto Portfolios")
        db_table = "crypto_portfolio"

    def __str__(self):
        return f"{self.user.email} - Portfolio (${self.total_value_usd})"

    def update_portfolio(self):
        """Update portfolio values based on current crypto prices."""
        from django.db.models import Sum

        wallets = self.user.crypto_wallets.filter(status="ACTIVE")
        total_value = Decimal("0.00")

        for wallet in wallets:
            current_price = wallet.cryptocurrency.current_price
            wallet_value = wallet.balance * current_price
            total_value += wallet_value

        self.total_value_usd = total_value
        self.total_profit_loss_usd = total_value - self.total_invested_usd

        if self.total_invested_usd > 0:
            self.total_profit_loss_percentage = (
                self.total_profit_loss_usd / self.total_invested_usd
            ) * 100

        self.save()


class CryptoWatchlist(models.Model):
    """
    User's cryptocurrency watchlist.
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="crypto_watchlist"
    )
    cryptocurrency = models.ForeignKey(
        Cryptocurrency, on_delete=models.CASCADE, related_name="watchers"
    )
    target_price = models.DecimalField(
        _("target price"), max_digits=20, decimal_places=8, null=True, blank=True
    )
    alert_enabled = models.BooleanField(_("alert enabled"), default=True)
    notes = models.TextField(_("notes"), blank=True)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)

    class Meta:
        verbose_name = _("Crypto Watchlist")
        verbose_name_plural = _("Crypto Watchlists")
        db_table = "crypto_watchlist"
        unique_together = ["user", "cryptocurrency"]

    def __str__(self):
        return f"{self.user.email} - {self.cryptocurrency.symbol} Watchlist"
