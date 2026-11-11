"""End-to-end workflows from the brief (E2E-01 to 04). Each checks what the user sees and what was stored."""

import re

import pytest
from django.core import mail
from playwright.sync_api import expect

from catalog.models import Category, Product
from orders.models import CartItem, Order, OrderStatus, Payment
from tests.conftest import sign_in_with_cookie
from tests.factories import ADMIN_USERNAME, PASSWORD, make_admin, make_customer, make_shop
from tests.pages import AdminLoginPage, CartPage, CheckoutPage, CustomerLoginPage, PaymentPage, ProductPage, RegisterPage

pytestmark = [pytest.mark.e2e, pytest.mark.django_db(transaction=True)]


def sign_out_customer(page):
    page.get_by_test_id("account-menu").click()
    page.get_by_test_id("logout-button").click()
    expect(page.get_by_test_id("toast").filter(has_text="signed out")).to_be_visible()


@pytest.mark.tc("E2E-01")
def test_customer_shopping_workflow(page, site):
    shop = make_shop()
    # Register, then sign out and sign in again as the brief's scenario does
    RegisterPage(page, site).open().register("Meera Iyer", "meera@example.com", "9812345678", "22 Temple Street, Madurai 625001", PASSWORD)
    expect(page.get_by_test_id("account-menu")).to_contain_text("Meera")
    sign_out_customer(page)
    CustomerLoginPage(page, site).open().sign_in("meera@example.com", PASSWORD)
    # Search, open the product, add it
    page.get_by_test_id("header-search-input").fill("earbuds")
    page.get_by_test_id("header-search-button").click()
    page.get_by_test_id("product-grid").get_by_test_id("product-link").filter(has_text="Arc Wireless Earbuds").click()
    ProductPage(page, site).add_to_cart(2)
    # Cart → review → place order → pay
    CartPage(page, site).open().check_out()
    expect(page.get_by_test_id("checkout-total")).to_have_text("₹4,998.00")
    CheckoutPage(page, site).place_order()
    payment = PaymentPage(page, site)
    order_id = payment.order_id()
    payment.pay("UPI", succeed=True)
    expect(page.get_by_test_id("confirmation-order-id")).to_have_text(order_id)
    expect(page.get_by_test_id("confirmation-status")).to_have_text("Confirmed")
    expect(page.get_by_test_id("confirmation-total")).to_have_text("₹4,998.00")
    sign_out_customer(page)
    # Stored results
    rows = Order.objects.filter(order_id=order_id)
    assert rows.count() == 1 and rows[0].order_status == OrderStatus.CONFIRMED and rows[0].amount == 4998
    assert Payment.objects.get(order_id=order_id).payment_status == "Success"
    assert Product.objects.get(pk=shop["Arc Wireless Earbuds"].pk).quantity == 8
    assert not CartItem.objects.filter(customer__email="meera@example.com").exists()
    assert len(mail.outbox) == 1 and order_id in mail.outbox[0].subject and "4,998.00" in mail.outbox[0].body


@pytest.mark.ai
@pytest.mark.tc("E2E-02")
def test_ai_recommendation_workflow(page, site):
    shop = make_shop()
    customer = make_customer()
    CustomerLoginPage(page, site).open().sign_in("asha@example.com", PASSWORD)
    ProductPage(page, site).open_product(shop["Electric Kettle"])
    similar = page.get_by_test_id("similar-products")
    expect(similar).to_be_visible()
    first = similar.get_by_test_id("rec-card").first
    picked = first.get_by_test_id("rec-name").inner_text().strip()
    first.get_by_test_id("rec-link").click()
    expect(page.get_by_test_id("product-title")).to_have_text(picked)
    ProductPage(page, site).add_to_cart(1)
    assert CartItem.objects.filter(customer=customer, product__product_name=picked).exists()


@pytest.mark.admin
@pytest.mark.tc("E2E-03")
def test_admin_product_management_workflow(page, site):
    make_admin()
    AdminLoginPage(page, site).open().sign_in(ADMIN_USERNAME, PASSWORD)
    # Add a category
    page.goto(f"{site}/manage/categories/")
    page.get_by_test_id("add-category").click()
    page.get_by_label("Category name").fill("Garden and Outdoors")
    page.get_by_test_id("save-category").click()
    expect(page.get_by_test_id("category-row").filter(has_text="Garden and Outdoors")).to_be_visible()
    # Add a product
    page.goto(f"{site}/manage/products/")
    page.get_by_test_id("add-product").click()
    page.get_by_label("Category").select_option(label="Garden and Outdoors")
    page.get_by_label("Product name").fill("Solar Garden Lights, Set of 4")
    page.get_by_label("Brand").fill("Lumora")
    page.get_by_label("Price (₹)").fill("899")
    page.get_by_label("Quantity in stock").fill("40")
    page.get_by_label("Description").fill("Stake lights that charge by day and glow for eight hours.")
    page.get_by_test_id("save-product").click()
    expect(page.get_by_test_id("toast").filter(has_text="Solar Garden Lights")).to_be_visible()  # lands on the admin product page
    page.goto(f"{site}/manage/products/")
    row = page.get_by_test_id("product-row").filter(has_text="Solar Garden Lights")
    expect(row).to_contain_text("₹899.00")
    # View it on the storefront
    product = Product.objects.get(product_name="Solar Garden Lights, Set of 4")
    page.goto(site + product.get_absolute_url())
    expect(page.get_by_test_id("product-title")).to_have_text("Solar Garden Lights, Set of 4")
    # Update it
    page.goto(f"{site}/manage/products/")
    page.get_by_test_id("product-row").filter(has_text="Solar Garden Lights").get_by_test_id("edit-product").click()
    page.get_by_label("Price (₹)").fill("799")
    page.get_by_test_id("save-product").click()
    expect(page.get_by_test_id("toast").filter(has_text="updated")).to_be_visible()
    page.goto(f"{site}/manage/products/")
    expect(page.get_by_test_id("product-row").filter(has_text="Solar Garden Lights")).to_contain_text("₹799.00")
    assert Product.objects.get(pk=product.pk).price == 799
    # Delete it
    page.get_by_test_id("product-row").filter(has_text="Solar Garden Lights").get_by_test_id("delete-product").click()
    page.get_by_test_id("confirm-ok").click()
    expect(page.get_by_test_id("product-row").filter(has_text="Solar Garden Lights")).to_have_count(0)
    assert not Product.objects.filter(pk=product.pk).exists()
    assert Category.objects.filter(category_name="Garden and Outdoors").exists()
    # Sign out
    page.get_by_test_id("admin-logout").click()
    expect(page).to_have_url(re.compile(r"/manage/login/"))


@pytest.mark.admin
@pytest.mark.customer
@pytest.mark.tc("E2E-04")
def test_order_management_workflow(page, site, browser, as_customer):
    shop = make_shop()
    admin = make_admin()
    customer = make_customer()
    # The customer places and pays an order
    as_customer(customer)
    CartItem.objects.create(customer=customer, product=shop["Pressure Cooker"], quantity=1)
    CartPage(page, site).open().check_out()
    CheckoutPage(page, site).place_order()
    payment = PaymentPage(page, site)
    order_id = payment.order_id()
    payment.pay("Card", succeed=True)
    expect(page.get_by_test_id("confirmation-status")).to_have_text("Confirmed")
    # The admin, in a separate browser session, sees it and ships it
    admin_context = browser.new_context()
    admin_page = admin_context.new_page()
    sign_in_with_cookie(admin_page, site, admin)
    admin_page.goto(f"{site}/manage/orders/")
    group = admin_page.get_by_test_id("order-group").filter(has_text=order_id)
    group.get_by_test_id("order-id").click()  # expand the ledger row
    group.get_by_test_id("open-order").click()
    admin_page.get_by_label("New status").select_option("Shipped")
    admin_page.get_by_test_id("update-status").click()
    expect(admin_page.get_by_test_id("toast").filter(has_text="now Shipped")).to_be_visible()
    admin_context.close()
    # The customer sees the new status
    page.goto(f"{site}/orders/{order_id}/")
    expect(page.get_by_test_id("order-detail-status")).to_have_text("Shipped")
    assert Order.objects.get(order_id=order_id).order_status == OrderStatus.SHIPPED
