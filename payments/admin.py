"""
Admin configuration for payments app.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    PaymentMethod,
    PaymentTransaction,
    PaystackCustomer,
    PaystackWebhook,
    Refund,
    PaymentNotification,
)


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "method_type",
        "get_display_name",
        "is_default",
        "status",
        "created_at",
    )
    list_filter = ("method_type", "status", "is_default", "created_at")
    search_fields = ("user__email", "nickname", "bank_name", "card_last4")
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "reference",
        "transaction_type",
        "user",
        "amount",
        "currency",
        "status",
        "created_at",
    )
    list_filter = ("transaction_type", "status", "currency", "created_at")
    search_fields = ("reference", "user__email", "paystack_reference", "description")
    readonly_fields = ("id", "reference", "created_at", "updated_at")


@admin.register(PaystackCustomer)
class PaystackCustomerAdmin(admin.ModelAdmin):
    list_display = ("user", "customer_code", "customer_email", "created_at")
    search_fields = ("user__email", "customer_code", "customer_email")
    readonly_fields = ("created_at", "updated_at")


@admin.register(PaystackWebhook)
class PaystackWebhookAdmin(admin.ModelAdmin):
    list_display = ("event_type", "reference", "processed", "created_at")
    list_filter = ("event_type", "processed", "created_at")
    search_fields = ("reference", "event_type")
    readonly_fields = ("id", "created_at", "processed_at")

    def has_add_permission(self, request):
        return False


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = (
        "reference",
        "original_transaction",
        "user",
        "amount",
        "status",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("reference", "user__email", "original_transaction__reference")
    readonly_fields = ("id", "reference", "created_at", "updated_at")


@admin.register(PaymentNotification)
class PaymentNotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "notification_type", "title", "is_read", "created_at")
    list_filter = (
        "notification_type",
        "is_read",
        "email_sent",
        "sms_sent",
        "created_at",
    )
    search_fields = ("user__email", "title", "message")
    readonly_fields = ("created_at", "read_at")
