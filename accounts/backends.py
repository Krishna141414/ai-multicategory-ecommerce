"""Customers sign in with their email address (brief: Login (email, password)).

The admin keeps Django's normal username login (ModelBackend, listed second in settings).
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

from accounts.models import Customer


class EmailBackend(ModelBackend):
    """Authenticate a customer by email + password. Inactive customers are refused."""

    def authenticate(self, request, email=None, password=None, **kwargs):
        if not email or password is None:
            return None
        customer = Customer.objects.select_related("user").filter(email__iexact=email.strip()).first()
        if customer is None:
            # Hash anyway so an unknown email takes as long as a wrong password (no account probing).
            get_user_model()().set_password(password)
            return None
        user = customer.user
        if user.check_password(password) and self.user_can_authenticate(user) and customer.is_active:
            return user
        return None
