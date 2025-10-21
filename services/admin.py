"""
Admin configuration for services app.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import ServiceProvider, ServiceCategory, AirtimeTopUp, BillPayment, SchoolFeePayment, ServiceTransaction, SavedService


@admin.register(ServiceProvider)
class ServiceProviderAdmin(admin.ModelAdmin):
    list_display = ('name', 'service_type', 'code', 'is_active', 'service_charge')
    list_filter = ('service_type', 'is_active', 'created_at')
    search_fields = ('name', 'code', 'description')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'is_active', 'display_order')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(AirtimeTopUp)
class AirtimeTopUpAdmin(admin.ModelAdmin):
    list_display = ('reference', 'user', 'phone_number', 'network', 'amount', 'status', 'created_at')
    list_filter = ('network', 'status', 'provider', 'created_at')
    search_fields = ('reference', 'user__email', 'phone_number')
    readonly_fields = ('id', 'reference', 'created_at', 'updated_at')


@admin.register(BillPayment)
class BillPaymentAdmin(admin.ModelAdmin):
    list_display = ('reference', 'user', 'bill_type', 'customer_name', 'amount', 'status', 'created_at')
    list_filter = ('bill_type', 'status', 'provider', 'created_at')
    search_fields = ('reference', 'user__email', 'customer_name', 'customer_id')
    readonly_fields = ('id', 'reference', 'created_at', 'updated_at')


@admin.register(SchoolFeePayment)
class SchoolFeePaymentAdmin(admin.ModelAdmin):
    list_display = ('reference', 'user', 'school_name', 'student_name', 'amount', 'status', 'created_at')
    list_filter = ('payment_type', 'status', 'created_at')
    search_fields = ('reference', 'user__email', 'school_name', 'student_name', 'student_id')
    readonly_fields = ('id', 'reference', 'created_at', 'updated_at')


@admin.register(ServiceTransaction)
class ServiceTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'service_type', 'service_id', 'amount', 'status', 'created_at')
    list_filter = ('service_type', 'status', 'created_at')
    search_fields = ('user__email', 'service_id')
    readonly_fields = ('id', 'created_at')


@admin.register(SavedService)
class SavedServiceAdmin(admin.ModelAdmin):
    list_display = ('user', 'provider', 'service_type', 'nickname', 'is_favorite', 'last_used')
    list_filter = ('service_type', 'is_favorite', 'created_at')
    search_fields = ('user__email', 'provider__name', 'nickname')
    readonly_fields = ('created_at', 'updated_at')