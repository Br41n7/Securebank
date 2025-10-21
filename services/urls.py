"""
URL configuration for services app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, api_views

# API router
router = DefaultRouter()
router.register(r'providers', api_views.ServiceProviderViewSet)
router.register(r'categories', api_views.ServiceCategoryViewSet)
router.register(r'saved', api_views.SavedServiceViewSet)

urlpatterns = [
    # API endpoints
    path('', include(router.urls)),
    
    # Airtime services
    path('airtime/topup/', views.AirtimeTopUpView.as_view(), name='airtime_topup'),
    path('airtime/providers/', views.AirtimeProvidersView.as_view(), name='airtime_providers'),
    path('airtime/validate/', views.ValidatePhoneNumberView.as_view(), name='validate_phone'),
    
    # Bill payments
    path('bills/pay/', views.PayBillView.as_view(), name='pay_bill'),
    path('bills/providers/', views.BillProvidersView.as_view(), name='bill_providers'),
    path('bills/validate/', views.ValidateCustomerView.as_view(), name='validate_customer'),
    path('bills/history/', views.BillHistoryView.as_view(), name='bill_history'),
    
    # School fees
    path('school/pay/', views.PaySchoolFeeView.as_view(), name='pay_school_fee'),
    path('school/validate/', views.ValidateSchoolView.as_view(), name='validate_school'),
    path('school/history/', views.SchoolFeeHistoryView.as_view(), name='school_fee_history'),
    
    # Saved services
    path('saved/', views.SavedServicesView.as_view(), name='saved_services'),
    path('saved/add/', views.SaveServiceView.as_view(), name='save_service'),
    path('saved/<int:pk>/remove/', views.RemoveSavedServiceView.as_view(), name='remove_saved_service'),
    
    # Service categories
    path('categories/', views.ServiceCategoriesView.as_view(), name='service_categories'),
    path('categories/<int:pk>/providers/', views.CategoryProvidersView.as_view(), name='category_providers'),
    
    # General
    path('search/', views.SearchServicesView.as_view(), name='search_services'),
    path('recent/', views.RecentServicesView.as_view(), name='recent_services'),
]