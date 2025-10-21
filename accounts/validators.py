"""
Custom validators for SecureBank accounts.
"""

import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class PasswordComplexityValidator:
    """
    Validates password complexity requirements.
    """
    def validate(self, password, user=None):
        errors = []
        
        # Check minimum length (handled by Django's MinimumLengthValidator)
        if len(password) < 12:
            errors.append(_("Password must be at least 12 characters long."))
        
        # Check for uppercase letters
        if not re.search(r'[A-Z]', password):
            errors.append(_("Password must contain at least one uppercase letter."))
        
        # Check for lowercase letters
        if not re.search(r'[a-z]', password):
            errors.append(_("Password must contain at least one lowercase letter."))
        
        # Check for digits
        if not re.search(r'\d', password):
            errors.append(_("Password must contain at least one digit."))
        
        # Check for special characters
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:"\\|,.<>\/?]', password):
            errors.append(_("Password must contain at least one special character."))
        
        # Check for common patterns
        if re.search(r'(.)\1{2,}', password):  # Three or more repeated characters
            errors.append(_("Password cannot contain three or more repeated characters in a row."))
        
        # Check for sequential characters
        if self.has_sequential_chars(password):
            errors.append(_("Password cannot contain sequential characters (e.g., '123', 'abc')."))
        
        if errors:
            raise ValidationError(errors)

    def get_help_text(self):
        return _(
            "Password must be at least 12 characters long and contain uppercase letters, "
            "lowercase letters, digits, and special characters. Avoid repeated or sequential characters."
        )

    def has_sequential_chars(self, password):
        """Check for sequential characters in password."""
        password_lower = password.lower()
        
        # Check for numeric sequences
        for i in range(len(password_lower) - 2):
            if (
                ord(password_lower[i]) + 1 == ord(password_lower[i + 1]) and
                ord(password_lower[i + 1]) + 1 == ord(password_lower[i + 2])
            ):
                return True
        
        return False


class AccountNumberValidator:
    """
    Validates account number format.
    """
    def __init__(self, length=10):
        self.length = length

    def __call__(self, value):
        if not value.isdigit():
            raise ValidationError(_("Account number must contain only digits."))
        
        if len(value) != self.length:
            raise ValidationError(_("Account number must be exactly {length} digits long.").format(length=self.length))
        
        # Check for repeated patterns
        if len(set(value)) < 3:
            raise ValidationError(_("Account number is too simple. Please use a different number."))


class PhoneNumberValidator:
    """
    Validates phone number format for international numbers.
    """
    def __call__(self, value):
        # Remove all non-digit characters
        clean_number = re.sub(r'[^\d]', '', value)
        
        if not clean_number:
            raise ValidationError(_("Phone number cannot be empty."))
        
        # Check minimum length (country code + number)
        if len(clean_number) < 10:
            raise ValidationError(_("Phone number is too short."))
        
        # Check maximum length
        if len(clean_number) > 15:
            raise ValidationError(_("Phone number is too long."))
        
        # Check if it starts with a valid country code or format
        if not (value.startswith('+') or value.startswith('0')):
            raise ValidationError(_("Phone number must start with '+' for international format or '0' for local format."))


class AmountValidator:
    """
    Validates transaction amounts.
    """
    def __init__(self, min_amount=0.01, max_amount=None):
        self.min_amount = min_amount
        self.max_amount = max_amount

    def __call__(self, value):
        if value <= 0:
            raise ValidationError(_("Amount must be greater than zero."))
        
        if value < self.min_amount:
            raise ValidationError(_("Minimum amount is {min_amount}.").format(min_amount=self.min_amount))
        
        if self.max_amount and value > self.max_amount:
            raise ValidationError(_("Maximum amount is {max_amount}.").format(max_amount=self.max_amount))
        
        # Check for too many decimal places
        if value.as_tuple().exponent < -2:
            raise ValidationError(_("Amount cannot have more than 2 decimal places."))


class KYCDocumentValidator:
    """
    Validates KYC document uploads.
    """
    def __call__(self, value):
        # Check file size (max 5MB)
        max_size = 5 * 1024 * 1024
        if value.size > max_size:
            raise ValidationError(_("File size cannot exceed 5MB."))
        
        # Check file extension
        allowed_extensions = ['jpg', 'jpeg', 'png', 'pdf']
        file_extension = value.name.split('.')[-1].lower()
        
        if file_extension not in allowed_extensions:
            raise ValidationError(_("Only JPG, PNG, and PDF files are allowed."))
        
        # Check MIME type
        allowed_mime_types = ['image/jpeg', 'image/png', 'application/pdf']
        if value.content_type not in allowed_mime_types:
            raise ValidationError(_("Invalid file type."))