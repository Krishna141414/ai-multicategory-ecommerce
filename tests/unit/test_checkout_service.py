"""Cart, Submit Cart and Dummy Payment rules (brief rules 4 and 5)."""

from decimal import Decimal

import pytest
from django.core import mail

from accounts.services import register_customer
from catalog.models import Category, Product, Status
from orders.models import CartItem, Order, OrderStatus, Payment
from orders.services import cart as cart_service
from orders.services.cart import CartError
from orders.services.checkout import CheckoutError, order_total, submit_cart
from orders.services.payment import FAILURE, SUCCESS, pay
from orders.services.status import set_order_status
from recommender.models import CustomerProductInteraction

pytestmark = [pytest.mark.unit, pytest.mark.django_db]


@pytest.fixture
def customer():
    return register_customer(name="Asha Rao", email="asha@example.com", password="Velora#Test-2026",
                             mobile_number="9876543210", address="14 Lakeview Apartments, Pune 411045")


@pytest.fixture
def products():
    cat = Category.objects.create(category_name="Electronics")
    earbuds = Product.objects.create(category=cat, product_name="Arc 3 Wireless Earbuds", brand="Sonvale",
                                     price=Decimal("2499.00"), description="Earbuds.", quantity=5)
    charger = Product.objects.create(category=cat, product_name="33 W USB-C Fast Charger", brand="Chargelink",
                                     price=Decimal("899.00"), description="Charger.", quantity=3)
    empty = Product.objects.create(category=cat, product_name="55-inch QLED Smart TV", brand="Lumora",
                                   price=Decimal("46990.00"), description="TV.", quantity=0)
    return earbuds, charger, empty


def stock(product):
    return Product.objects.get(pk=product.pk).quantity


# --- cart -------------------------------------------------------------------------

def test_add_to_cart_blocks_zero_stock(customer, products):
    with pytest.raises(CartError):
        cart_service.add_to_cart(customer, products[2], 1)
    assert not CartItem.objects.exists()


def test_cart_qty_cannot_exceed_stock(customer, products):
    earbuds = products[0]
    cart_service.add_to_cart(customer, earbuds, 4)
    with pytest.raises(CartError):
        cart_service.add_to_cart(customer, earbuds, 2)  # 4 + 2 > 5
    item = CartItem.objects.get()
    with pytest.raises(CartError):
        cart_service.update_quantity(customer, item.pk, 6)
    assert CartItem.objects.get().quantity == 4


def test_add_merges_lines_and_logs_cart_interaction(customer, products):
    cart_service.add_to_cart(customer, products[0], 1)
    cart_service.add_to_cart(customer, products[0], 1)
    cart_service.add_to_cart(customer, products[1], 1)
    summary = cart_service.get_cart(customer)
    assert summary.count == 3 and len(summary.lines) == 2
    assert summary.total == Decimal("2499.00") * 2 + Decimal("899.00")
    assert CustomerProductInteraction.objects.filter(interaction_type="cart").count() == 3


def test_inactive_product_cannot_be_added(customer, products):
    products[0].status = Status.INACTIVE
    products[0].save()
    with pytest.raises(CartError):
        cart_service.add_to_cart(customer, products[0], 1)


def test_remove_item(customer, products):
    item = cart_service.add_to_cart(customer, products[0], 1)
    assert cart_service.remove_item(customer, item.pk) == "Arc 3 Wireless Earbuds"
    assert not CartItem.objects.exists()


# --- submit cart --------------------------------------------------------------------

def test_submit_creates_one_row_per_item_with_shared_order_id(customer, products):
    cart_service.add_to_cart(customer, products[0], 2)
    cart_service.add_to_cart(customer, products[1], 1)
    order_id = submit_cart(customer, "key-1")
    rows = Order.objects.filter(order_id=order_id).order_by("id")
    assert rows.count() == 2 and len({r.id for r in rows}) == 2
    assert {r.order_status for r in rows} == {OrderStatus.PENDING}
    assert [r.product_name for r in rows] == ["Arc 3 Wireless Earbuds", "33 W USB-C Fast Charger"]


def test_amount_and_total(customer, products):
    cart_service.add_to_cart(customer, products[0], 2)
    cart_service.add_to_cart(customer, products[1], 3)
    order_id = submit_cart(customer, "key-1")
    amounts = {r.product_name: r.amount for r in Order.objects.filter(order_id=order_id)}
    assert amounts["Arc 3 Wireless Earbuds"] == Decimal("4998.00")
    assert amounts["33 W USB-C Fast Charger"] == Decimal("2697.00")
    assert order_total(order_id) == Decimal("7695.00")


def test_stock_reserved_on_submit_and_cart_kept(customer, products):
    cart_service.add_to_cart(customer, products[0], 2)
    submit_cart(customer, "key-1")
    assert stock(products[0]) == 3
    assert CartItem.objects.count() == 1  # cleared only after payment


def test_submit_rolls_back_when_one_item_short(customer, products):
    earbuds, charger, _ = products
    cart_service.add_to_cart(customer, earbuds, 2)
    cart_service.add_to_cart(customer, charger, 3)
    Product.objects.filter(pk=charger.pk).update(quantity=1)  # someone else bought 2 meanwhile
    with pytest.raises(CheckoutError):
        submit_cart(customer, "key-1")
    assert not Order.objects.exists()
    assert stock(earbuds) == 5 and stock(charger) == 1


def test_submit_rejects_inactive_product(customer, products):
    cart_service.add_to_cart(customer, products[0], 1)
    Product.objects.filter(pk=products[0].pk).update(status=Status.INACTIVE)
    with pytest.raises(CheckoutError):
        submit_cart(customer, "key-1")
    assert not Order.objects.exists()


def test_resubmit_same_key_returns_same_order(customer, products):
    cart_service.add_to_cart(customer, products[0], 1)
    first = submit_cart(customer, "key-1")
    second = submit_cart(customer, "key-1")  # double click / refresh
    assert first == second and Order.objects.count() == 1 and stock(products[0]) == 4


def test_new_checkout_releases_older_unpaid_order(customer, products):
    cart_service.add_to_cart(customer, products[0], 2)
    first = submit_cart(customer, "key-1")
    second = submit_cart(customer, "key-2")  # went back, checked out again without paying
    assert first != second
    assert set(Order.objects.filter(order_id=first).values_list("order_status", flat=True)) == {OrderStatus.CANCELLED}
    assert stock(products[0]) == 3  # reserved once, not twice


def test_empty_cart_cannot_be_submitted(customer):
    with pytest.raises(CheckoutError):
        submit_cart(customer, "key-1")


# --- payment ------------------------------------------------------------------------

def test_payment_success_confirms_and_clears_cart_and_emails(customer, products, django_capture_on_commit_callbacks):
    cart_service.add_to_cart(customer, products[0], 2)
    order_id = submit_cart(customer, "key-1")
    with django_capture_on_commit_callbacks(execute=True):
        result = pay(customer, order_id, "UPI", SUCCESS)
    assert result.succeeded and not result.already_paid
    assert set(Order.objects.filter(order_id=order_id).values_list("order_status", flat=True)) == {OrderStatus.CONFIRMED}
    payment = Payment.objects.get(order_id=order_id)
    assert payment.payment_status == Payment.Status.SUCCESS and payment.total_amount == Decimal("4998.00")
    assert payment.customer == customer and payment.payment_method == "UPI"
    assert not CartItem.objects.exists()
    assert CustomerProductInteraction.objects.filter(interaction_type="purchase").count() == 1
    assert len(mail.outbox) == 1
    email = mail.outbox[0]
    assert order_id in email.subject and email.to == ["asha@example.com"]
    assert "Arc 3 Wireless Earbuds" in email.body and "₹4,998.00" in email.body and "Confirmed" in email.body


def test_payment_failure_keeps_pending(customer, products, django_capture_on_commit_callbacks):
    cart_service.add_to_cart(customer, products[0], 1)
    order_id = submit_cart(customer, "key-1")
    with django_capture_on_commit_callbacks(execute=True):
        result = pay(customer, order_id, "Card", FAILURE)
    assert not result.succeeded
    assert set(Order.objects.filter(order_id=order_id).values_list("order_status", flat=True)) == {OrderStatus.PENDING}
    assert Payment.objects.get().payment_status == Payment.Status.FAILED
    assert CartItem.objects.count() == 1 and len(mail.outbox) == 0
    # retry succeeds
    assert pay(customer, order_id, "Card", SUCCESS).succeeded


def test_pay_twice_is_idempotent(customer, products):
    cart_service.add_to_cart(customer, products[0], 1)
    order_id = submit_cart(customer, "key-1")
    pay(customer, order_id, "UPI", SUCCESS)
    again = pay(customer, order_id, "UPI", SUCCESS)
    assert again.already_paid
    assert Payment.objects.filter(payment_status=Payment.Status.SUCCESS).count() == 1
    assert Order.objects.filter(order_id=order_id).count() == 1


def test_cannot_pay_someone_elses_order(customer, products):
    other = register_customer(name="Ravi K", email="ravi@example.com", password="Velora#Test-2026",
                              mobile_number="9123456780", address="5 MG Road, Kochi 682016")
    cart_service.add_to_cart(customer, products[0], 1)
    order_id = submit_cart(customer, "key-1")
    with pytest.raises(CheckoutError):
        pay(other, order_id, "UPI", SUCCESS)


def test_cancel_restores_stock(customer, products):
    cart_service.add_to_cart(customer, products[0], 2)
    order_id = submit_cart(customer, "key-1")
    assert stock(products[0]) == 3
    set_order_status(order_id, OrderStatus.CANCELLED)
    assert stock(products[0]) == 5
    with pytest.raises(CheckoutError):
        pay(customer, order_id, "UPI", SUCCESS)
