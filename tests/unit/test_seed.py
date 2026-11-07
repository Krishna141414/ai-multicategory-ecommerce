"""The demo data commands load the brief's categories and are safe to run twice."""

import pytest
from django.core.management import call_command

from accounts.models import Customer
from catalog.models import Category, Product
from catalog.seed_data import CATEGORIES
from orders.models import Order

pytestmark = [pytest.mark.unit, pytest.mark.django_db]

BRIEF_CATEGORIES = [
    "Electronics", "Fashion and Clothing", "Home and Furniture", "Books and Stationery",
    "Beauty and Personal Care", "Sports and Fitness", "Mobile Phones and Accessories",
    "Computers and Laptops", "Toys and Games", "Kitchen and Home Appliances",
]


def test_seed_categories_match_the_brief_exactly():
    assert [name for name, _ in CATEGORIES] == BRIEF_CATEGORIES


def test_seed_demo_is_idempotent(monkeypatch):
    monkeypatch.setenv("ADMIN_USERNAME", "admin")
    monkeypatch.setenv("ADMIN_PASSWORD", "Admin#test-123")
    monkeypatch.setenv("DEMO_CUSTOMER_PASSWORD", "Demo#test-123")
    call_command("create_default_admin")
    call_command("seed_demo")
    first = (Category.objects.count(), Product.objects.count(), Customer.objects.count(), Order.objects.count())
    call_command("seed_demo")
    second = (Category.objects.count(), Product.objects.count(), Customer.objects.count(), Order.objects.count())
    assert first == second
    assert first[0] == 10 and first[1] >= 100 and first[2] == 4
    assert Product.objects.filter(quantity=0).exists()
    assert Product.objects.filter(is_sponsored=True).count() >= 8
