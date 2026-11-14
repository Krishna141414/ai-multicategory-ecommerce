"""Database-level rules from the brief (price > 0, quantity >= 0, amount = price × quantity, unique email)."""

from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction

from accounts.models import Customer
from catalog.models import Category, Product
from orders.models import Order

pytestmark = [pytest.mark.unit, pytest.mark.django_db]


def make_product(**overrides) -> Product:
    category = Category.objects.create(category_name="Electronics")
    data = dict(category=category, product_name="Test earbuds", brand="Sonvale", price=Decimal("999.00"),
                description="Wireless earbuds.", quantity=5)
    data.update(overrides)
    return Product.objects.create(**data)


def make_customer(email="asha@example.com") -> Customer:
    user = User.objects.create_user(username=email, email=email, password="Secret#12345")
    return Customer.objects.create(user=user, name="Asha Rao", email=email, mobile_number="9876543210", address="Pune")


def test_price_must_be_positive():
    with pytest.raises(IntegrityError), transaction.atomic():
        make_product(price=Decimal("0"))


def test_quantity_cannot_be_negative():
    with pytest.raises(IntegrityError), transaction.atomic():
        make_product(quantity=-1)


def test_order_amount_is_price_times_quantity():
    product = make_product()
    order = Order.objects.create(order_id="ORD-TEST-0001", customer=make_customer(), product=product,
                                 product_name=product.product_name, quantity=3, price=product.price)
    assert order.amount == Decimal("2997.00")


def test_duplicate_email_case_insensitive():
    make_customer("asha@example.com")
    other = User.objects.create_user(username="asha2", password="Secret#12345")
    with pytest.raises(IntegrityError), transaction.atomic():
        Customer.objects.create(user=other, name="Asha", email="ASHA@Example.com", mobile_number="9876543210", address="Pune")


def test_new_customer_is_active_by_default():
    assert make_customer().status == Customer.Status.ACTIVE


def test_product_needs_exactly_one_category():
    # brief rule 2: each product belongs to one category; a category in use can't be deleted from under it
    from django.db.models import ProtectedError

    with pytest.raises(IntegrityError), transaction.atomic():
        Product.objects.create(category=None, product_name="No aisle", brand="Sonvale", price=Decimal("10.00"),
                               description="x", quantity=1)
    product = make_product()
    with pytest.raises(ProtectedError):
        product.category.delete()
