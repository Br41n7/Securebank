"""
Views for accounts app.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin


class LoginView(TemplateView):
    template_name = 'login.html'
    
    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'success': True, 'redirect': '/dashboard/'})
        else:
            return JsonResponse({'success': False, 'message': 'Invalid credentials'})


class LogoutView(TemplateView):
    def get(self, request):
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
        return redirect('home')


class RegisterView(TemplateView):
    template_name = 'register.html'
    
    def post(self, request):
        # Handle registration logic
        return JsonResponse({'success': True, 'message': 'Registration successful'})


class VerifyEmailView(TemplateView):
    template_name = 'verify_email.html'


class VerifyPhoneView(TemplateView):
    template_name = 'verify_phone.html'


class ForgotPasswordView(TemplateView):
    template_name = 'forgot_password.html'


class ResetPasswordView(TemplateView):
    template_name = 'reset_password.html'


class ChangePasswordView(LoginRequiredMixin, TemplateView):
    template_name = 'change_password.html'


class SetupTwoFactorView(LoginRequiredMixin, TemplateView):
    template_name = 'setup_2fa.html'


class VerifyTwoFactorView(TemplateView):
    template_name = 'verify_2fa.html'


class DisableTwoFactorView(LoginRequiredMixin, TemplateView):
    template_name = 'disable_2fa.html'


class SubmitKYCView(LoginRequiredMixin, TemplateView):
    template_name = 'submit_kyc.html'


class KYCStatusView(LoginRequiredMixin, TemplateView):
    template_name = 'kyc_status.html'


class SecuritySettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'security_settings.html'


class RefreshTokenView(TemplateView):
    def post(self, request):
        return JsonResponse({'success': True, 'token': 'new_token'})