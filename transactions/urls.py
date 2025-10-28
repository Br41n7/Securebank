"""
URL configuration for transactions app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, api_views

# API router
router = DefaultRouter()
router.register(r"transactions", api_views.TransactionViewSet)
router.register(r"beneficiaries", api_views.BeneficiaryViewSet)
router.register(r"scheduled", api_views.ScheduledTransactionViewSet)
router.register(r"limits", api_views.TransactionLimitViewSet)

urlpatterns = [
    # API endpoints
    path("", include(router.urls)),
    # Transaction operations
    path("transfer/", views.TransferView.as_view(), name="transfer"),
    path("deposit/", views.DepositView.as_view(), name="deposit"),
    path("withdraw/", views.WithdrawView.as_view(), name="withdraw"),
    # Transaction verification
    path("verify-otp/", views.VerifyOTPView.as_view(), name="verify_otp"),
    path("resend-otp/", views.ResendOTPView.as_view(), name="resend_otp"),
    # Transaction history
    path(
        "history/", views.TransactionHistoryView.as_view(), name="transaction_history"
    ),
    path("statement/", views.AccountStatementView.as_view(), name="account_statement"),
    # Beneficiaries
    path(
        "beneficiaries/", views.BeneficiaryListView.as_view(), name="beneficiary_list"
    ),
    path(
        "beneficiaries/add/", views.AddBeneficiaryView.as_view(), name="add_beneficiary"
    ),
    # Scheduled transactions
    path(
        "scheduled/",
        views.ScheduledTransactionListView.as_view(),
        name="scheduled_transactions",
    ),
    path(
        "scheduled/add/",
        views.CreateScheduledTransactionView.as_view(),
        name="create_scheduled_transaction",
    ),
]
