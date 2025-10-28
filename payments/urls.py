"""
URL configuration for payments app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, api_views

# API router
router = DefaultRouter()
router.register(r"methods", api_views.PaymentMethodViewSet)
router.register(r"transactions", api_views.PaymentTransactionViewSet)
router.register(r"customers", api_views.PaystackCustomerViewSet)
router.register(r"refunds", api_views.RefundViewSet)

urlpatterns = [
    # API endpoints
    path("", include(router.urls)),
    # Payment operations
    path(
        "initialize/", views.InitializePaymentView.as_view(), name="initialize_payment"
    ),
    path("verify/", views.VerifyPaymentView.as_view(), name="verify_payment"),
    path("charge/", views.ChargePaymentView.as_view(), name="charge_payment"),
    # Payment methods
    path("methods/", views.PaymentMethodListView.as_view(), name="payment_methods"),
    path(
        "methods/add/", views.AddPaymentMethodView.as_view(), name="add_payment_method"
    ),
    path(
        "methods/<uuid:pk>/remove/",
        views.RemovePaymentMethodView.as_view(),
        name="remove_payment_method",
    ),
    path(
        "methods/<uuid:pk>/set-default/",
        views.SetDefaultPaymentMethodView.as_view(),
        name="set_default_payment_method",
    ),
    # Refunds
    path("refund/", views.RequestRefundView.as_view(), name="request_refund"),
    path("refunds/", views.RefundListView.as_view(), name="refund_list"),
    # Notifications
    path(
        "notifications/",
        views.PaymentNotificationListView.as_view(),
        name="payment_notifications",
    ),
    path(
        "notifications/<int:pk>/mark-read/",
        views.MarkNotificationReadView.as_view(),
        name="mark_notification_read",
    ),
]
