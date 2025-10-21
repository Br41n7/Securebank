"""
URL configuration for giftcards app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, api_views

# API router
router = DefaultRouter()
router.register(r'types', api_views.GiftCardTypeViewSet)
router.register(r'cards', api_views.GiftCardViewSet)
router.register(r'transactions', api_views.GiftCardTransactionViewSet)
router.register(r'rates', api_views.GiftCardRateViewSet)
router.register(r'disputes', api_views.GiftCardDisputeViewSet)

urlpatterns = [
    # API endpoints
    path('', include(router.urls)),
    
    # Gift card operations
    path('sell/', views.SellGiftCardView.as_view(), name='sell_giftcard'),
    path('buy/', views.BuyGiftCardView.as_view(), name='buy_giftcard'),
    path('trade/', views.TradeGiftCardView.as_view(), name='trade_giftcard'),
    
    # Card management
    path('cards/upload/', views.UploadGiftCardView.as_view(), name='upload_giftcard'),
    path('cards/<uuid:pk>/verify/', views.VerifyGiftCardView.as_view(), name='verify_giftcard'),
    path('cards/<uuid:pk>/status/', views.GiftCardStatusView.as_view(), name='giftcard_status'),
    
    # Rates and pricing
    path('rates/current/', views.CurrentRatesView.as_view(), name='current_rates'),
    path('rates/calculate/', views.CalculateRateView.as_view(), name='calculate_rate'),
    
    # Transactions
    path('transactions/', views.GiftCardTransactionListView.as_view(), name='giftcard_transactions'),
    path('transactions/<uuid:pk>/details/', views.TransactionDetailsView.as_view(), name='transaction_details'),
    
    # Disputes
    path('disputes/create/', views.CreateDisputeView.as_view(), name='create_dispute'),
    path('disputes/', views.DisputeListView.as_view(), name='dispute_list'),
    
    # Inventory
    path('inventory/', views.InventoryView.as_view(), name='giftcard_inventory'),
]