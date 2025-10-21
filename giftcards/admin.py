"""
Admin configuration for giftcards app.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import GiftCardType, GiftCard, GiftCardTransaction, GiftCardRate, GiftCardDispute, GiftCardInventory


@admin.register(GiftCardType)
class GiftCardTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'buy_rate', 'sell_rate', 'is_active')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(GiftCard)
class GiftCardAdmin(admin.ModelAdmin):
    list_display = ('gift_card_type', 'face_value', 'seller', 'status', 'offered_price', 'created_at')
    list_filter = ('status', 'condition', 'country', 'created_at')
    search_fields = ('seller__email', 'gift_card_type__name', 'card_code')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(GiftCardTransaction)
class GiftCardTransactionAdmin(admin.ModelAdmin):
    list_display = ('reference', 'transaction_type', 'seller', 'amount', 'status', 'created_at')
    list_filter = ('transaction_type', 'status', 'created_at')
    search_fields = ('reference', 'seller__email', 'gift_card__gift_card_type__name')
    readonly_fields = ('id', 'reference', 'created_at', 'updated_at')


@admin.register(GiftCardRate)
class GiftCardRateAdmin(admin.ModelAdmin):
    list_display = ('gift_card_type', 'buy_rate', 'sell_rate', 'valid_from', 'is_active')
    list_filter = ('is_active', 'valid_from')
    search_fields = ('gift_card_type__name',)
    readonly_fields = ('created_at',)


@admin.register(GiftCardDispute)
class GiftCardDisputeAdmin(admin.ModelAdmin):
    list_display = ('transaction', 'raised_by', 'dispute_type', 'status', 'created_at')
    list_filter = ('dispute_type', 'status', 'created_at')
    search_fields = ('transaction__reference', 'raised_by__email', 'description')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(GiftCardInventory)
class GiftCardInventoryAdmin(admin.ModelAdmin):
    list_display = ('gift_card_type', 'face_value', 'quantity', 'selling_price', 'is_available')
    list_filter = ('is_available', 'created_at')
    search_fields = ('gift_card_type__name',)
    readonly_fields = ('created_at', 'updated_at')