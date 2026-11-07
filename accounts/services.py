"""Account helpers shared by views and management commands."""

import os

from django.contrib.auth.models import User
from django.db import transaction

from accounts.models import Customer

DEACTIVATED_MESSAGE = "Your account has been deactivated. Please contact support."
INVALID_LOGIN_MESSAGE = "Email or password is incorrect."


def ensure_default_admin(reset_password: bool = False) -> tuple[User, bool]:
    """Create the store admin from ADMIN_USERNAME / ADMIN_PASSWORD / ADMIN_EMAIL in .env.

    Returns (user, created). An existing admin keeps its password unless `reset_password`.
    """
    username = os.getenv("ADMIN_USERNAME", "").strip()
    password = os.getenv("ADMIN_PASSWORD", "")
    email = os.getenv("ADMIN_EMAIL", "").strip()
    if not username or not password:
        raise ValueError("Set ADMIN_USERNAME and ADMIN_PASSWORD in .env first.")
    user, created = User.objects.get_or_create(username=username, defaults={"email": email})
    user.is_staff = True
    user.is_superuser = True
    user.is_active = True
    if email:
        user.email = email
    if created or reset_password:
        user.set_password(password)
    user.save()
    return user, created


def default_admin() -> User | None:
    """The admin who receives customer queries (the first staff account)."""
    return User.objects.filter(is_staff=True, is_active=True).order_by("id").first()


@transaction.atomic
def register_customer(*, name: str, email: str, password: str, mobile_number: str, address: str) -> Customer:
    """Create a User (hashed password) and its Customer profile. New customers are Active."""
    email = email.strip().lower()
    user = User.objects.create_user(username=email, email=email, password=password, first_name=name.split()[0])
    return Customer.objects.create(user=user, name=name.strip(), email=email, mobile_number=mobile_number,
                                   address=address.strip())
