"""
Admin configuration for transactions app.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    Transaction,
    TransactionLog,
    Beneficiary,
    TransactionLimit,
    ScheduledTransaction,
)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "reference",
        "transaction_type",
        "source_account",
        "amount",
        "currency",
        "status",
        "created_at",
    )
    list_filter = ("transaction_type", "status", "currency", "priority", "created_at")
    search_fields = ("reference", "user__email", "recipient_name", "description")
    readonly_fields = ("id", "reference", "created_at", "updated_at")

    fieldsets = (
        (
            _("Transaction Info"),
            {"fields": ("reference", "transaction_type", "priority", "status")},
        ),
        (_("Accounts"), {"fields": ("source_account", "destination_account")}),
        (
            _("Amounts"),
            {"fields": ("amount", "currency", "fee", "tax", "total_amount")},
        ),
        (
            _("Recipient"),
            {"fields": ("recipient_name", "recipient_account", "recipient_bank")},
        ),
        (_("Details"), {"fields": ("description", "narration")}),
        (_("Security"), {"fields": ("requires_otp", "otp_verified", "verified_by")}),
        (_("Metadata"), {"fields": ("ip_address", "user_agent", "device_id")}),
        (
            _("Timestamps"),
            {"fields": ("created_at", "processed_at", "completed_at", "updated_at")},
        ),
    )


@admin.register(TransactionLog)
class TransactionLogAdmin(admin.ModelAdmin):
    list_display = ("transaction", "action", "old_status", "new_status", "created_at")
    list_filter = ("action", "created_at")
    search_fields = ("transaction__reference", "details")
    readonly_fields = ("created_at",)

    def has_add_permission(self, request):
        return False


@admin.register(Beneficiary)
class BeneficiaryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "account_number",
        "bank_name",
        "user",
        "beneficiary_type",
        "is_favorite",
    )
    list_filter = ("beneficiary_type", "is_favorite", "created_at")
    search_fields = ("name", "account_number", "bank_name", "user__email")
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(TransactionLimit)
class TransactionLimitAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "tier",
        "daily_transfer_limit",
        "single_transfer_limit",
        "monthly_transfer_limit",
    )
    list_filter = ("tier", "created_at")
    search_fields = ("user__email",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(ScheduledTransaction)
class ScheduledTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "beneficiary_name",
        "amount",
        "frequency",
        "status",
        "next_execution",
    )
    list_filter = ("frequency", "status", "created_at")
    search_fields = ("user__email", "beneficiary_name", "beneficiary_account")
    readonly_fields = ("id", "created_at", "updated_at")
