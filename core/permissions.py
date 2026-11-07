"""Role checks used by every view.

- `customer_required`: logged-in, active customer (admins get 403, guests go to login).
- `admin_required`: logged-in staff user (customers get 403, guests go to admin login).
"""

from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.urls import reverse

from accounts.models import Customer


def get_customer(request) -> Customer | None:
    """The active Customer behind this request, or None."""
    user = request.user
    if not user.is_authenticated or user.is_staff:
        return None
    customer = getattr(user, "customer", None)
    return customer if customer is not None and customer.is_active else None


def is_admin(user) -> bool:
    return user.is_authenticated and user.is_staff


def customer_required(view_func):
    """Allow only an authenticated, active customer; set `request.customer`."""

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path(), reverse("accounts:login"))
        customer = get_customer(request)
        if customer is None:
            raise PermissionDenied("This page is for customer accounts.")
        request.customer = customer
        return view_func(request, *args, **kwargs)

    return wrapper


def admin_required(view_func):
    """Allow only staff users (the store admin)."""

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path(), reverse("adminpanel:login"))
        if not request.user.is_staff:
            raise PermissionDenied("This page is for the store admin.")
        return view_func(request, *args, **kwargs)

    return wrapper
