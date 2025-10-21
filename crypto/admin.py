"""
Admin configuration for crypto app.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Cryptocurrency, CryptoWallet, CryptoTransaction, CryptoPriceHistory, CryptoPortfolio, CryptoWatchlist


@admin.register(Cryptocurrency)
class CryptocurrencyAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'name', 'current_price', 'market_cap', 'is_active')
    list_filter = ('crypto_type', 'is_active', 'created_at')
    search_fields = ('symbol', 'name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(CryptoWallet)
class CryptoWalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'cryptocurrency', 'wallet_address', 'balance', 'status', 'is_default')
    list_filter = ('wallet_type', 'status', 'is_default', 'created_at')
    search_fields = ('user__email', 'cryptocurrency__symbol', 'wallet_address')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(CryptoTransaction)
class CryptoTransactionAdmin(admin.ModelAdmin):
    list_display = ('reference', 'user', 'cryptocurrency', 'transaction_type', 'amount', 'status', 'created_at')
    list_filter = ('transaction_type', 'status', 'cryptocurrency', 'created_at')
    search_fields = ('reference', 'user__email', 'blockchain_tx_hash')
    readonly_fields = ('id', 'reference', 'created_at', 'updated_at')


@admin.register(CryptoPriceHistory)
class CryptoPriceHistoryAdmin(admin.ModelAdmin):
    list_display = ('cryptocurrency', 'price', 'market_cap', 'timestamp')
    list_filter = ('cryptocurrency', 'timestamp')
    readonly_fields = ('timestamp',)
    
    def has_add_permission(self, request):
        return False


@admin.register(CryptoPortfolio)
class CryptoPortfolioAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_value_usd', 'total_invested_usd', 'total_profit_loss_usd', 'last_updated')
    search_fields = ('user__email',)
    readonly_fields = ('last_updated',)


@admin.register(CryptoWatchlist)
class CryptoWatchlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'cryptocurrency', 'target_price', 'alert_enabled', 'created_at')
    list_filter = ('alert_enabled', 'created_at')
    search_fields = ('user__email', 'cryptocurrency__symbol')
    readonly_fields = ('created_at',)