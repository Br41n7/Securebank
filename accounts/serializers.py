"""
Serializers for accounts app.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserProfile, BankAccount, Beneficiary

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "phone_number",
            "date_of_birth",
            "is_verified",
            "is_phone_verified",
            "two_factor_enabled",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "is_verified",
            "is_phone_verified",
            "created_at",
            "updated_at",
        ]


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            "user",
            "gender",
            "address",
            "city",
            "state",
            "country",
            "postal_code",
            "id_type",
            "id_number",
            "kyc_status",
            "currency",
            "language",
            "timezone",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["kyc_status", "created_at", "updated_at"]


class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = [
            "id",
            "account_number",
            "account_name",
            "account_type",
            "currency",
            "balance",
            "available_balance",
            "frozen_balance",
            "daily_limit",
            "single_transaction_limit",
            "status",
            "is_default",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "account_number",
            "balance",
            "available_balance",
            "frozen_balance",
            "created_at",
            "updated_at",
        ]


class BeneficiarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Beneficiary
        fields = [
            "id",
            "name",
            "account_number",
            "bank_name",
            "bank_code",
            "beneficiary_type",
            "is_favorite",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
