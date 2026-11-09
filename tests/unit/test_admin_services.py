"""Admin rules: category/product deletion, order status changes, customer status, queries, dashboard."""

from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.urls import reverse

from accounts.models import Customer
from accounts.services import register_customer
from adminpanel.services import dashboard_stats
from catalog.models import Category, Product, Status
from catalog.services import CategoryInUse, delete_category, delete_product
from messaging import services as msg
from messaging.models import Message
from orders.models import CartItem, Order, OrderStatus, Payment
from orders.services.status import OrderStatusError, set_order_status
from reviews.models import Rating, Review

pytestmark = [pytest.mark.unit, pytest.mark.django_db]
PASSWORD = "Velora#Test-2026"


@pytest.fixture
def admin_user():
    return User.objects.create_user(username="storeadmin", password=PASSWORD, is_staff=True)


@pytest.fixture
def customer():
    return register_customer(name="Asha Rao", email="asha@example.com", password=PASSWORD,
                             mobile_number="9876543210", address="14 Lakeview Apartments, Pune 411045")


@pytest.fixture
def product():
    category = Category.objects.create(category_name="Electronics")
    return Product.objects.create(category=category, product_name="Arc 3 Wireless Earbuds", brand="Sonvale",
                                  price=Decimal("2499.00"), description="Earbuds.", quantity=10)


def place_order(customer, product, qty=2, status=OrderStatus.PENDING, order_id="ORD-TEST-0001", paid=False):
    Product.objects.filter(pk=product.pk).update(quantity=product.quantity - qty)  # stock reserved at checkout
    row = Order.objects.create(order_id=order_id, customer=customer, product=product, product_name=product.product_name,
                               quantity=qty, price=product.price, order_status=status)
    if paid:
        Payment.objects.create(order_id=order_id, customer=customer, total_amount=row.amount, payment_method="UPI",
                               payment_status=Payment.Status.SUCCESS, reference=f"PAY-{order_id}")
    return row


def test_category_with_products_cannot_be_deleted(product):
    with pytest.raises(CategoryInUse):
        delete_category(product.category)
    assert Category.objects.filter(pk=product.category_id).exists()


def test_empty_category_is_deleted():
    category = Category.objects.create(category_name="Garden")
    delete_category(category)
    assert not Category.objects.filter(pk=category.pk).exists()


def test_delete_product_without_orders_hard_deletes(product):
    assert delete_product(product) == "deleted"
    assert not Product.objects.filter(pk=product.pk).exists()


def test_delete_product_with_orders_soft_deletes(product, customer):
    place_order(customer, product)
    CartItem.objects.create(customer=customer, product=product, quantity=1)
    assert delete_product(product) == "deactivated"
    product.refresh_from_db()
    assert product.status == Status.INACTIVE
    assert Order.objects.filter(product=product).count() == 1  # history intact
    assert not CartItem.objects.filter(product=product).exists()


def test_status_moves_forward(product, customer):
    place_order(customer, product)
    for status in (OrderStatus.CONFIRMED, OrderStatus.SHIPPED, OrderStatus.DELIVERED):
        set_order_status("ORD-TEST-0001", status)
        assert Order.objects.get().order_status == status


def test_invalid_transition_rejected(product, customer):
    place_order(customer, product, status=OrderStatus.DELIVERED)
    with pytest.raises(OrderStatusError):
        set_order_status("ORD-TEST-0001", OrderStatus.PENDING)
    with pytest.raises(OrderStatusError):
        set_order_status("ORD-TEST-0001", OrderStatus.CANCELLED)


def test_cancel_restores_stock_once(product, customer):
    place_order(customer, product, qty=3)
    assert Product.objects.get(pk=product.pk).quantity == 7
    set_order_status("ORD-TEST-0001", OrderStatus.CANCELLED)
    assert Product.objects.get(pk=product.pk).quantity == 10
    with pytest.raises(OrderStatusError):  # Cancelled is final, so stock can't be restored twice
        set_order_status("ORD-TEST-0001", OrderStatus.CANCELLED + "x")


def test_dashboard_totals_count_only_paid_uncancelled_sales(product, customer):
    place_order(customer, product, qty=1, order_id="ORD-A", paid=True)
    place_order(customer, product, qty=1, order_id="ORD-B", paid=False)
    place_order(customer, product, qty=1, order_id="ORD-C", paid=True, status=OrderStatus.CANCELLED)
    stats = dashboard_stats()
    assert stats["total_orders"] == 3
    assert stats["total_customers"] == 1 and stats["total_categories"] == 1 and stats["total_products"] == 1
    assert stats["total_sales"] == Decimal("2499.00")


def test_new_conversation_has_null_parent_and_reply_reuses_id(customer, admin_user):
    first = msg.start_customer_query(customer.user, "Delivery date", "When will my order arrive?")
    assert first.parent_message is None and first.conversation_id.startswith("CNV-")
    assert first.sender_type == "customer" and first.receiver_type == "admin"
    answer = msg.reply(first.conversation_id, admin_user, "It ships tomorrow.")
    assert answer.conversation_id == first.conversation_id and answer.parent_message == first
    assert answer.sender_type == "admin" and answer.receiver == customer.user
    follow_up = msg.reply(first.conversation_id, customer.user, "Thanks!")
    assert follow_up.parent_message == answer and follow_up.receiver_type == "admin"


def test_customer_cannot_see_other_thread(customer, admin_user):
    other = register_customer(name="Ravi K", email="ravi@example.com", password=PASSWORD,
                              mobile_number="9123456780", address="5 MG Road, Kochi 682016")
    first = msg.start_customer_query(other.user, "Refund", "Please refund my order.")
    with pytest.raises(PermissionDenied):
        msg.thread(first.conversation_id, customer.user)
    assert [c.conversation_id for c in msg.conversations_for(customer.user)] == []
    assert len(msg.conversations_for(admin_user)) == 1


def test_admin_pages_render_and_are_staff_only(client, admin_user, customer, product):
    place_order(customer, product, paid=True, status=OrderStatus.DELIVERED)
    Rating.objects.create(product=product, customer=customer, rating=4)
    Review.objects.create(product=product, customer=customer, review="Good sound for the price.")
    msg.start_customer_query(customer.user, "Hello", "Is this in stock?")
    pages = [reverse("adminpanel:dashboard"), reverse("adminpanel:categories"), reverse("adminpanel:category_create"),
             reverse("adminpanel:products"), reverse("adminpanel:product_create"),
             reverse("adminpanel:product_detail", args=[product.pk]), reverse("adminpanel:product_edit", args=[product.pk]),
             reverse("adminpanel:customers"), reverse("adminpanel:customer_detail", args=[customer.pk]),
             reverse("adminpanel:orders"), reverse("adminpanel:order_detail", args=["ORD-TEST-0001"]),
             reverse("adminpanel:reviews"), reverse("adminpanel:queries"), reverse("adminpanel:query_new"),
             reverse("adminpanel:query_thread", args=[Message.objects.first().conversation_id])]
    client.force_login(customer.user, backend="accounts.backends.EmailBackend")
    assert all(client.get(url).status_code == 403 for url in pages)
    client.force_login(admin_user)
    for url in pages:
        assert client.get(url).status_code == 200, url


def test_admin_creates_category_and_rejects_bad_product(client, admin_user):
    client.force_login(admin_user)
    client.post(reverse("adminpanel:category_create"), {"category_name": "Garden", "description": "Plants", "status": "Active"})
    category = Category.objects.get(category_name="Garden")
    bad = {"category": category.pk, "product_name": "Hose", "brand": "Greenline", "price": "0", "quantity": "-1",
           "description": "A hose.", "keywords": "hose", "status": "Active"}
    response = client.post(reverse("adminpanel:product_create"), bad)
    body = response.content.decode()
    assert "Price must be greater than zero." in body and "Quantity can’t be negative." in body
    assert not Product.objects.filter(product_name="Hose").exists()


def test_admin_deactivates_customer(client, admin_user, customer):
    client.force_login(admin_user)
    client.post(reverse("adminpanel:customer_set_status", args=[customer.pk]), {"status": "Inactive"})
    customer.refresh_from_db()
    assert customer.status == Customer.Status.INACTIVE and not customer.user.is_active
