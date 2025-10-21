"""
Views for transactions app.
"""

from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse


class TransferView(LoginRequiredMixin, TemplateView):
    template_name = 'transfer.html'
    
    def post(self, request):
        return JsonResponse({'success': True, 'message': 'Transfer initiated'})


class DepositView(LoginRequiredMixin, TemplateView):
    template_name = 'deposit.html'


class WithdrawView(LoginRequiredMixin, TemplateView):
    template_name = 'withdraw.html'


class VerifyOTPView(TemplateView):
    def post(self, request):
        return JsonResponse({'success': True, 'message': 'OTP verified'})


class ResendOTPView(TemplateView):
    def post(self, request):
        return JsonResponse({'success': True, 'message': 'OTP resent'})


class TransactionHistoryView(LoginRequiredMixin, TemplateView):
    template_name = 'transaction_history.html'


class AccountStatementView(LoginRequiredMixin, TemplateView):
    template_name = 'account_statement.html'


class BeneficiaryListView(LoginRequiredMixin, TemplateView):
    template_name = 'beneficiary_list.html'


class AddBeneficiaryView(LoginRequiredMixin, TemplateView):
    template_name = 'add_beneficiary.html'


class ScheduledTransactionListView(LoginRequiredMixin, TemplateView):
    template_name = 'scheduled_transactions.html'


class CreateScheduledTransactionView(LoginRequiredMixin, TemplateView):
    template_name = 'create_scheduled_transaction.html'