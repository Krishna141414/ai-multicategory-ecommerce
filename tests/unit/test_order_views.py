"""Cart / checkout / payment / order pages through the Django test client."""

from decimal import Decimal

import pytest
from django.urls import reverse

from accounts.services import register_customer
from catalog.models import Category, Product
from orders.models import CartItem, Order, Payment

pytestmark = [pytest.mark.unit, pytest.mark.django_db]


@pytest.fixture
def customer():
    return register_customer(name="Asha Rao", email="asha@example.com", password="Velora#Test-2026",
                             mobile_number="9876543210", address="14 Lakeview Apartments, Pune 411045")


@pytest.fixture
def product():
    cat = Category.objects.create(category_name="Electronics")
    return Product.objects.create(category=cat, product_name="Arc 3 Wireless Earbuds", brand="Sonvale",
                                  price=Decimal("2499.00"), description="Earbuds.", quantity=5)


@pytest.fixture
def signed_in(client, customer):
    client.force_login(customer.user, backend="accounts.backends.EmailBackend")
    return client


def test_cart_requires_login(client, product):
    assert reverse("accounts:login") in client.get(reverse("orders:cart"))["Location"]
    response = client.post(reverse("orders:cart_add", args=[product.pk]), {"quantity": 1})
    assert response.status_code == 302 and reverse("accounts:login") in response["Location"]


def test_add_to_cart_json(signed_in, product):
    response = signed_in.post(reverse("orders:cart_add", args=[product.pk]), {"quantity": 2}, HTTP_ACCEPT="application/json")
    assert response.json() == {"ok": True, "message": "Added Arc 3 Wireless Earbuds to your cart.", "count": 2,
                               "cart_url": reverse("orders:cart")}
    response = signed_in.post(reverse("orders:cart_add", args=[product.pk]), {"quantity": 9}, HTTP_ACCEPT="application/json")
    assert response.status_code == 400 and response.json()["ok"] is False


def test_full_flow_pages(signed_in, customer, product):
    signed_in.post(reverse("orders:cart_add", args=[product.pk]), {"quantity": 2})
    assert "Arc 3 Wireless Earbuds" in signed_in.get(reverse("orders:cart")).content.decode()
    page = signed_in.get(reverse("orders:checkout"))
    key = page.context["checkout_key"]
    response = signed_in.post(reverse("orders:checkout"), {"checkout_key": key})
    order_id = Order.objects.get().order_id
    assert response["Location"] == reverse("orders:payment", args=[order_id])
    # double submit of the same review page returns the same order
    signed_in.post(reverse("orders:checkout"), {"checkout_key": key})
    assert Order.objects.values("order_id").distinct().count() == 1
    failed = signed_in.post(reverse("orders:payment", args=[order_id]), {"payment_method": "Card", "outcome": "failure"})
    assert "Payment failed" in failed.content.decode()
    done = signed_in.post(reverse("orders:payment", args=[order_id]), {"payment_method": "UPI", "outcome": "success"})
    assert done["Location"] == reverse("orders:confirmation", args=[order_id])
    body = signed_in.get(done["Location"]).content.decode()
    assert order_id in body and "₹4,998.00" in body and "Confirmed" in body
    assert not CartItem.objects.exists()
    assert order_id in signed_in.get(reverse("orders:history")).content.decode()
    assert "Confirmed" in signed_in.get(reverse("orders:detail", args=[order_id])).content.decode()
    assert Payment.objects.filter(order_id=order_id).count() == 2


def test_customer_cannot_open_another_customers_order(client, customer, product):
    other = register_customer(name="Ravi K", email="ravi@example.com", password="Velora#Test-2026",
                              mobile_number="9123456780", address="5 MG Road, Kochi 682016")
    Order.objects.create(order_id="ORD-OTHER-0001", customer=other, product=product, product_name=product.product_name,
                         quantity=1, price=product.price)
    client.force_login(customer.user, backend="accounts.backends.EmailBackend")
    for name in ("orders:detail", "orders:payment", "orders:confirmation"):
        assert client.get(reverse(name, args=["ORD-OTHER-0001"])).status_code == 404


def test_stale_checkout_key_is_rejected(signed_in, product):
    signed_in.post(reverse("orders:cart_add", args=[product.pk]), {"quantity": 1})
    signed_in.get(reverse("orders:checkout"))
    response = signed_in.post(reverse("orders:checkout"), {"checkout_key": "forged"})
    assert response["Location"] == reverse("orders:checkout") and not Order.objects.exists()
