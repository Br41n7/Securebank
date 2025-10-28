"""
URL configuration for crypto app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, api_views

# API router
router = DefaultRouter()
router.register(r"wallets", api_views.CryptoWalletViewSet)
router.register(r"transactions", api_views.CryptoTransactionViewSet)
router.register(r"cryptocurrencies", api_views.CryptocurrencyViewSet)
router.register(r"portfolio", api_views.CryptoPortfolioViewSet)
router.register(r"watchlist", api_views.CryptoWatchlistViewSet)

urlpatterns = [
    # API endpoints
    path("", include(router.urls)),
    # Crypto operations
    path("buy/", views.BuyCryptoView.as_view(), name="buy_crypto"),
    path("sell/", views.SellCryptoView.as_view(), name="sell_crypto"),
    path("send/", views.SendCryptoView.as_view(), name="send_crypto"),
    path("receive/", views.ReceiveCryptoView.as_view(), name="receive_crypto"),
    path("swap/", views.SwapCryptoView.as_view(), name="swap_crypto"),
    # Wallet operations
    path("wallets/create/", views.CreateWalletView.as_view(), name="create_wallet"),
    path(
        "wallets/<uuid:pk>/balance/",
        views.WalletBalanceView.as_view(),
        name="wallet_balance",
    ),
    path(
        "wallets/<uuid:pk>/address/",
        views.WalletAddressView.as_view(),
        name="wallet_address",
    ),
    # Market data
    path("market/prices/", views.MarketPricesView.as_view(), name="market_prices"),
    path(
        "market/history/<str:symbol>/",
        views.PriceHistoryView.as_view(),
        name="price_history",
    ),
    # Portfolio
    path(
        "portfolio/summary/",
        views.PortfolioSummaryView.as_view(),
        name="portfolio_summary",
    ),
    path(
        "portfolio/performance/",
        views.PortfolioPerformanceView.as_view(),
        name="portfolio_performance",
    ),
    # Watchlist
    path("watchlist/add/", views.AddToWatchlistView.as_view(), name="add_to_watchlist"),
    path(
        "watchlist/remove/",
        views.RemoveFromWatchlistView.as_view(),
        name="remove_from_watchlist",
    ),
]
