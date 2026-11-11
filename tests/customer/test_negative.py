"""Negative cases beyond the brief's list (TC-NEG-01 to 08): the app must refuse safely and say why."""

import re

import pytest
from playwright.sync_api import expect

from accounts.models import Customer
from accounts.services import set_customer_status
from catalog.models import Category, Product
from messaging.services import start_customer_query
from orders.models import CartItem, Order, OrderStatus, Payment
from tests.factories import PASSWORD, make_admin, make_customer, make_shop
from tests.pages import CartPage, CheckoutPage, CustomerLoginPage, ProductPage, RegisterPage

pytestmark = [pytest.mark.negative, pytest.mark.django_db(transaction=True)]


@pytest.mark.customer
@pytest.mark.tc("TC-NEG-01")
def test_duplicate_email_registration(page, site):
    make_customer()
    RegisterPage(page, site).open().register("Another Asha", "ASHA@example.com", "9811111111", "1 Hill Road, Shimla 171001", PASSWORD)
    expect(page.get_by_test_id("error-email")).to_be_visible()
    assert Customer.objects.filter(email__iexact="asha@example.com").count() == 1


@pytest.mark.customer
@pytest.mark.tc("TC-NEG-02")
def test_deactivated_customer_cannot_log_in(page, site):
    set_customer_status(make_customer(), "Inactive")
    CustomerLoginPage(page, site).open().sign_in("asha@example.com", PASSWORD)
    expect(page.get_by_test_id("login-error")).to_contain_text("deactivated")
    expect(page.get_by_test_id("account-menu")).to_have_count(0)


@pytest.mark.customer
@pytest.mark.tc("TC-NEG-03")
def test_out_of_stock_product_cannot_be_added(page, site, as_customer):
    shop = make_shop()
    as_customer(make_customer())
    ProductPage(page, site).open_product(shop["4K Smart TV"])
    expect(page.get_by_test_id("stock-status")).to_contain_text("Out of stock")
    expect(page.get_by_test_id("add-to-cart")).to_have_count(0)


@pytest.mark.customer
@pytest.mark.tc("TC-NEG-04")
def test_cart_quantity_cannot_exceed_stock(page, site, as_customer):
    shop = make_shop()
    customer = make_customer()
    as_customer(customer)
    item = CartItem.objects.create(customer=customer, product=shop["Hand Blender"], quantity=1)  # 9 in stock
    cart = CartPage(page, site).open()
    cart.set_quantity("Hand Blender", 50)
    expect(page.get_by_test_id("toast").filter(has_text=re.compile("only|stock|available|up to", re.I))).to_be_visible()
    item.refresh_from_db()
    assert item.quantity == 1


@pytest.mark.customer
@pytest.mark.tc("TC-NEG-05")
def test_payment_failure_does_not_confirm(page, site, as_customer):
    shop = make_shop()
    customer = make_customer()
    as_customer(customer)
    CartItem.objects.create(customer=customer, product=shop["Electric Kettle"], quantity=1)
    CartPage(page, site).open().check_out()
    CheckoutPage(page, site).place_order()
    order_id = page.get_by_test_id("payment-order-id").inner_text().strip()
    page.get_by_test_id("method-card").check()
    page.get_by_test_id("outcome-failure").check()
    page.get_by_test_id("pay-button").click()
    expect(page.get_by_test_id("payment-failed")).to_contain_text("Payment failed")
    assert Order.objects.get(order_id=order_id).order_status == OrderStatus.PENDING
    assert Payment.objects.get(order_id=order_id).payment_status == "Failed"
    assert CartItem.objects.filter(customer=customer).exists()  # kept so the customer can retry


@pytest.mark.customer
@pytest.mark.tc("TC-NEG-06")
def test_customer_cannot_open_admin_pages(page, site, as_customer):
    as_customer(make_customer())
    response = page.goto(f"{site}/manage/")
    assert response.status == 403
    expect(page.get_by_role("heading", level=1)).to_contain_text("isn’t for this account")


@pytest.mark.customer
@pytest.mark.tc("TC-NEG-07")
def test_customer_cannot_see_another_customers_conversation(page, site, as_customer):
    make_admin()
    other = make_customer("Ravi Kumar", "ravi@example.com", "9123456780", "5 MG Road, Kochi 682016")
    private = start_customer_query(other.user, "Ravi's private question", "Is the trimmer waterproof?")
    as_customer(make_customer())
    response = page.goto(f"{site}/queries/{private.conversation_id}/")
    assert response.status == 403
    expect(page.get_by_text("Is the trimmer waterproof?")).to_have_count(0)


@pytest.mark.admin
@pytest.mark.tc("TC-NEG-08")
def test_invalid_price_and_negative_quantity_rejected(page, site, as_admin):
    Category.objects.create(category_name="Electronics")
    as_admin(make_admin())
    page.goto(f"{site}/manage/products/new/")
    page.get_by_label("Category").select_option(label="Electronics")
    page.get_by_label("Product name").fill("Broken Speaker")
    page.get_by_label("Brand").fill("Sonvale")
    page.get_by_label("Price (₹)").fill("0")
    page.get_by_label("Quantity in stock").fill("-1")
    page.get_by_label("Description").fill("Should never be saved.")
    page.get_by_test_id("save-product").click()
    expect(page.get_by_test_id("error-price")).to_be_visible()
    expect(page.get_by_test_id("error-quantity")).to_be_visible()
    assert not Product.objects.filter(product_name="Broken Speaker").exists()
