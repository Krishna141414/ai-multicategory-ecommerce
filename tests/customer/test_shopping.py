"""Customer shopping: categories, search, product pages, cart, checkout, dummy payment and orders (TC-CUS-06 to 20)."""

import re

import pytest
from playwright.sync_api import expect

from catalog.models import Product
from orders.models import CartItem, Order, OrderStatus, Payment
from tests.factories import make_customer, make_order, make_shop
from tests.pages import CartPage, CheckoutPage, PaymentPage, ProductPage

pytestmark = [pytest.mark.customer, pytest.mark.django_db(transaction=True)]


def names_on_page(page) -> list[str]:
    return [n.strip() for n in page.get_by_test_id("product-grid").get_by_test_id("product-name").all_inner_texts()]


@pytest.fixture
def shop():
    return make_shop()


@pytest.fixture
def customer(as_customer):
    c = make_customer()
    as_customer(c)
    return c


@pytest.mark.tc("TC-CUS-06")
def test_view_product_categories(page, site, shop):
    page.goto(f"{site}/categories/")
    tiles = page.get_by_test_id("category-tile")
    expect(tiles).to_have_count(2)
    expect(tiles.filter(has_text="Electronics")).to_contain_text("4 products")
    expect(tiles.filter(has_text="Kitchen and Home Appliances")).to_contain_text("3 products")


@pytest.mark.tc("TC-CUS-07")
def test_search_product_by_name(page, site, shop):
    page.goto(f"{site}/products/")
    page.get_by_label("Search", exact=True).fill("kettle")
    page.get_by_test_id("search-submit").click()
    expect(page.get_by_test_id("results-count")).to_contain_text("1")
    assert names_on_page(page) == ["Electric Kettle"]


@pytest.mark.tc("TC-CUS-08")
def test_search_product_by_category(page, site, shop):
    page.goto(f"{site}/products/")
    page.get_by_label("Category").select_option(label="Kitchen and Home Appliances")
    page.get_by_test_id("search-submit").click()
    expect(page.get_by_test_id("results-count")).to_contain_text("3")
    assert sorted(names_on_page(page)) == ["Electric Kettle", "Hand Blender", "Pressure Cooker"]


@pytest.mark.tc("TC-CUS-09")
def test_search_product_by_price(page, site, shop):
    page.goto(f"{site}/products/")
    page.get_by_label("Min price (₹)").fill("1500")
    page.get_by_label("Max price (₹)").fill("7000")
    page.get_by_test_id("search-submit").click()
    expect(page.get_by_test_id("product-grid")).to_be_visible()
    found = names_on_page(page)
    assert sorted(found) == ["Arc Wireless Earbuds", "Field Over-Ear Headphones", "Pocket Bluetooth Speaker", "Pressure Cooker"]
    assert all(1500 <= Product.objects.get(product_name=n).price <= 7000 for n in found)


@pytest.mark.tc("TC-CUS-10")
def test_view_products(page, site, shop):
    page.goto(f"{site}/products/")
    cards = page.get_by_test_id("product-grid").get_by_test_id("product-card")
    expect(cards).to_have_count(len(shop))
    first = cards.first
    expect(first.get_by_test_id("product-name")).not_to_be_empty()
    expect(first.get_by_test_id("product-price")).to_contain_text("₹")
    expect(first.get_by_role("img")).to_be_visible()


@pytest.mark.tc("TC-CUS-11")
def test_view_product_details(page, site, shop):
    product = shop["Arc Wireless Earbuds"]
    ProductPage(page, site).open_product(product)
    expect(page.get_by_test_id("product-title")).to_have_text("Arc Wireless Earbuds")
    expect(page.get_by_test_id("product-category-link")).to_have_text("Electronics")
    expect(page.get_by_test_id("product-brand")).to_have_text("Sonvale")
    expect(page.get_by_test_id("product-price")).to_have_text("₹2,499.00")
    expect(page.get_by_test_id("product-description")).to_contain_text("noise cancelling")
    expect(page.get_by_test_id("product-image")).to_be_visible()
    expect(page.get_by_test_id("available-quantity")).to_have_text("10 available")
    expect(page.get_by_test_id("product-rating")).to_contain_text("No ratings yet")


@pytest.mark.tc("TC-CUS-12")
def test_add_to_cart(page, site, shop, customer):
    product = shop["Arc Wireless Earbuds"]
    ProductPage(page, site).open_product(product).add_to_cart(2)
    expect(page.get_by_test_id("cart-count").first).to_have_text("2")
    assert CartItem.objects.get(customer=customer, product=product).quantity == 2


@pytest.mark.tc("TC-CUS-13")
def test_view_cart(page, site, shop, customer):
    CartItem.objects.create(customer=customer, product=shop["Arc Wireless Earbuds"], quantity=2)
    CartItem.objects.create(customer=customer, product=shop["Electric Kettle"], quantity=1)
    cart = CartPage(page, site).open()
    expect(page.get_by_test_id("cart-item")).to_have_count(2)
    expect(cart.line("Arc Wireless Earbuds").get_by_test_id("cart-item-total")).to_have_text("₹4,998.00")
    expect(cart.line("Electric Kettle").get_by_test_id("cart-item-total")).to_have_text("₹1,099.00")
    expect(cart.total()).to_have_text("₹6,097.00")  # 2 × 2,499 + 1,099


@pytest.mark.tc("TC-CUS-14")
def test_update_cart_quantity(page, site, shop, customer):
    item = CartItem.objects.create(customer=customer, product=shop["Electric Kettle"], quantity=1)
    cart = CartPage(page, site).open()
    cart.set_quantity("Electric Kettle", 3)
    expect(cart.line("Electric Kettle").get_by_test_id("cart-item-total")).to_have_text("₹3,297.00")
    expect(cart.total()).to_have_text("₹3,297.00")
    item.refresh_from_db()
    assert item.quantity == 3


@pytest.mark.tc("TC-CUS-15")
def test_remove_from_cart(page, site, shop, customer):
    CartItem.objects.create(customer=customer, product=shop["Electric Kettle"], quantity=1)
    CartItem.objects.create(customer=customer, product=shop["Hand Blender"], quantity=1)
    cart = CartPage(page, site).open()
    cart.remove("Hand Blender")
    expect(cart.toast("Removed Hand Blender")).to_be_visible()
    expect(page.get_by_test_id("cart-item")).to_have_count(1)
    expect(cart.total()).to_have_text("₹1,099.00")
    assert not CartItem.objects.filter(customer=customer, product=shop["Hand Blender"]).exists()


def _submit_cart(page, site, shop, customer):
    CartItem.objects.create(customer=customer, product=shop["Arc Wireless Earbuds"], quantity=2)
    CartItem.objects.create(customer=customer, product=shop["Electric Kettle"], quantity=1)
    CartPage(page, site).open().check_out()
    expect(page.get_by_test_id("checkout-total")).to_have_text("₹6,097.00")
    CheckoutPage(page, site).place_order()
    return PaymentPage(page, site)


@pytest.mark.tc("TC-CUS-16")
def test_submit_cart(page, site, shop, customer):
    payment = _submit_cart(page, site, shop, customer)
    order_id = payment.order_id()
    rows = Order.objects.filter(order_id=order_id)
    assert rows.count() == 2  # one row per cart item, one shared order_id, each with its own id
    assert len({r.pk for r in rows}) == 2
    assert {r.order_status for r in rows} == {OrderStatus.PENDING}
    assert sum(r.amount for r in rows) == 6097
    shop["Arc Wireless Earbuds"].refresh_from_db()
    assert shop["Arc Wireless Earbuds"].quantity == 8  # stock reserved
    expect(page.get_by_test_id("payment-total")).to_have_text("₹6,097.00")


@pytest.mark.tc("TC-CUS-17")
def test_dummy_payment(page, site, shop, customer):
    payment = _submit_cart(page, site, shop, customer)
    order_id = payment.order_id()
    payment.pay("UPI", succeed=True)
    expect(page).to_have_url(re.compile(rf"/orders/{order_id}/confirmed/"))
    paid = Payment.objects.get(order_id=order_id)
    assert paid.payment_status == "Success" and paid.payment_method == "UPI" and paid.total_amount == 6097
    assert set(Order.objects.filter(order_id=order_id).values_list("order_status", flat=True)) == {OrderStatus.CONFIRMED}
    assert not CartItem.objects.filter(customer=customer).exists()  # cleared only after the payment succeeded


@pytest.mark.tc("TC-CUS-18")
def test_view_order_confirmation(page, site, shop, customer):
    payment = _submit_cart(page, site, shop, customer)
    order_id = payment.order_id()
    payment.pay("Card", succeed=True)
    expect(page.get_by_test_id("confirmation-order-id")).to_have_text(order_id)
    expect(page.get_by_test_id("confirmation-status")).to_have_text("Confirmed")
    expect(page.get_by_test_id("confirmation-total")).to_have_text("₹6,097.00")
    expect(page.get_by_test_id("confirmation-items").get_by_role("row")).to_have_count(4)  # head, 2 items, total


@pytest.mark.tc("TC-CUS-19")
def test_view_order_history(page, site, shop, customer):
    make_order(customer, [(shop["Electric Kettle"], 1)], OrderStatus.DELIVERED, "ORD-20261001-AAAA")
    make_order(customer, [(shop["Hand Blender"], 2)], OrderStatus.SHIPPED, "ORD-20261020-BBBB")
    page.goto(f"{site}/orders/")
    rows = page.get_by_test_id("order-history-row")
    expect(rows).to_have_count(2)
    expect(rows.filter(has_text="ORD-20261001-AAAA").get_by_test_id("order-status")).to_have_text("Delivered")
    expect(rows.filter(has_text="ORD-20261020-BBBB").get_by_test_id("order-status")).to_have_text("Shipped")


@pytest.mark.tc("TC-CUS-20")
def test_view_order_details(page, site, shop, customer):
    order_id = make_order(customer, [(shop["Electric Kettle"], 2), (shop["Hand Blender"], 1)], OrderStatus.CONFIRMED)
    page.goto(f"{site}/orders/")
    page.get_by_test_id("order-link").filter(has_text=order_id).click()
    expect(page.get_by_test_id("order-detail-title")).to_contain_text(order_id)
    expect(page.get_by_test_id("order-detail-item")).to_have_count(2)
    expect(page.get_by_test_id("order-detail-total")).to_have_text("₹3,497.00")  # 2 × 1,099 + 1,299
    expect(page.get_by_test_id("order-detail-status")).to_have_text("Confirmed")
