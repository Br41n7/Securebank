"""
Custom authentication backends for SecureBank.
"""

try:
    import jwt
except ImportError:
    jwt = None

from django.conf import settings
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

User = get_user_model()


class EmailBackend(BaseBackend):
    """
    Custom authentication backend that allows users to log in using their email address.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(email=username)
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        except User.DoesNotExist:
            return None
        return None

    def get_user(self, user_id):
        try:
            user = User.objects.get(pk=user_id)
            if self.user_can_authenticate(user):
                return user
            return None
        except User.DoesNotExist:
            return None

    def user_can_authenticate(self, user):
        """
        Reject users with is_active=False and check if account is locked.
        """
        is_active = getattr(user, "is_active", False)
        if not is_active:
            return False

        # Check if account is locked
        if user.is_account_locked():
            return False

        return True


class JWTAuthentication(BaseAuthentication):
    """
    JWT authentication for API endpoints.
    """

    def authenticate(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION")

        if not auth_header or not auth_header.startswith("Bearer "):
            return None

        token = auth_header.split(" ")[1]

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = payload.get("user_id")

            if not user_id:
                raise AuthenticationFailed("Token payload invalid")

            user = User.objects.get(id=user_id)

            if not user.is_active:
                raise AuthenticationFailed("User account is disabled")

            if user.is_account_locked():
                raise AuthenticationFailed("User account is locked")

            return (user, token)

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token has expired")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Invalid token")
        except User.DoesNotExist:
            raise AuthenticationFailed("User not found")
        except Exception as e:
            raise AuthenticationFailed(f"Authentication failed: {str(e)}")

    def authenticate_header(self, request):
        return "Bearer"


class TwoFactorAuthentication(BaseAuthentication):
    """
    Two-factor authentication for sensitive operations.
    """

    def authenticate(self, request):
        # This would work with django-two-factor-auth
        # For now, we'll delegate to the main authentication
        pass


def generate_jwt_token(user):
    """
    Generate JWT token for authenticated user.
    """
    payload = {
        "user_id": str(user.id),
        "email": user.email,
        "is_staff": user.is_staff,
        "is_verified": user.is_verified,
        "exp": jwt.datetime.datetime.utcnow() + jwt.datetime.timedelta(hours=24),
        "iat": jwt.datetime.datetime.utcnow(),
    }

    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def refresh_jwt_token(token):
    """
    Refresh JWT token if it's still valid.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")

        if not user_id:
            raise AuthenticationFailed("Token payload invalid")

        user = User.objects.get(id=user_id)

        if not user.is_active:
            raise AuthenticationFailed("User account is disabled")

        # Generate new token
        return generate_jwt_token(user)

    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed("Token has expired and cannot be refreshed")
    except jwt.InvalidTokenError:
        raise AuthenticationFailed("Invalid token")
    except User.DoesNotExist:
        raise AuthenticationFailed("User not found")
