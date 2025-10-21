"""
URL configuration for accounts app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, api_views

# API router
router = DefaultRouter()
router.register(r'users', api_views.UserViewSet)
router.register(r'profiles', api_views.UserProfileViewSet)
router.register(r'accounts', api_views.BankAccountViewSet)
router.register(r'beneficiaries', api_views.BeneficiaryViewSet)

urlpatterns = [
    # API endpoints
    path('', include(router.urls)),
    
    # Authentication endpoints
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('verify-email/', views.VerifyEmailView.as_view(), name='verify_email'),
    path('verify-phone/', views.VerifyPhoneView.as_view(), name='verify_phone'),
    path('forgot-password/', views.ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/', views.ResetPasswordView.as_view(), name='reset_password'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    
    # Two-factor authentication
    path('2fa/setup/', views.SetupTwoFactorView.as_view(), name='setup_2fa'),
    path('2fa/verify/', views.VerifyTwoFactorView.as_view(), name='verify_2fa'),
    path('2fa/disable/', views.DisableTwoFactorView.as_view(), name='disable_2fa'),
    
    # KYC endpoints
    path('kyc/submit/', views.SubmitKYCView.as_view(), name='submit_kyc'),
    path('kyc/status/', views.KYCStatusView.as_view(), name='kyc_status'),
    
    # Security settings
    path('security/', views.SecuritySettingsView.as_view(), name='security_settings'),
    
    # JWT endpoints
    path('token/refresh/', views.RefreshTokenView.as_view(), name='token_refresh'),
]