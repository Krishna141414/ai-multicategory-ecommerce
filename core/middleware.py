"""Log out a customer whose account was deactivated while they were signed in."""

from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect

DEACTIVATED_MESSAGE = "Your account has been deactivated. Please contact support."


class ActiveCustomerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        if user.is_authenticated and not user.is_staff:
            customer = getattr(user, "customer", None)
            if customer is not None and not customer.is_active:
                logout(request)
                messages.error(request, DEACTIVATED_MESSAGE)
                return redirect("accounts:login")
        return self.get_response(request)
