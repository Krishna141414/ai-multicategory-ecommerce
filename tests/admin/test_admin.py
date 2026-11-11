"""Admin panel (TC-ADM-01 to 22)."""

import re

import pytest
from playwright.sync_api import expect

from accounts.services import set_customer_status
from catalog.models import Category, Product
from messaging.models import Message
from messaging.services import reply, start_customer_query
from orders.models import Order, OrderStatus
from reviews.models import Rating, Review
from tests.factories import ADMIN_USERNAME, PASSWORD, make_admin, make_customer, make_order, make_shop
from tests.pages import AdminLoginPage

pytestmark = [pytest.mark.admin, pytest.mark.django_db(transaction=True)]


@pytest.fixture
def admin(as_admin):
    user = make_admin()
    as_admin(user)
    return user


def toast(page, text):
    return page.get_by_test_id("toast").filter(has_text=text)


def confirm(page):
    page.get_by_test_id("confirm-ok").click()


@pytest.mark.tc("TC-ADM-01")
def test_admin_login(page, site):
    make_admin()
    AdminLoginPage(page, site).open().sign_in(ADMIN_USERNAME, PASSWORD)
    expect(page.get_by_test_id("admin-dashboard-heading")).to_be_visible()
    expect(page.get_by_test_id("admin-username")).to_contain_text(ADMIN_USERNAME)


@pytest.mark.negative
@pytest.mark.tc("TC-ADM-02")
def test_invalid_admin_login(page, site):
    make_admin()
    AdminLoginPage(page, site).open().sign_in(ADMIN_USERNAME, "not-the-password")
    expect(page.get_by_test_id("admin-login-error")).to_be_visible()
    expect(page).to_have_url(re.compile(r"/manage/login/"))


@pytest.mark.tc("TC-ADM-03")
def test_view_dashboard(page, site, admin):
    shop = make_shop()
    asha = make_customer()
    make_customer("Ravi Kumar", "ravi@example.com", "9123456780", "5 MG Road, Kochi 682016")
    make_order(asha, [(shop["Electric Kettle"], 2)], OrderStatus.DELIVERED, "ORD-20261001-AAAA")       # ₹2,198 paid
    make_order(asha, [(shop["Hand Blender"], 1)], OrderStatus.CANCELLED, "ORD-20261002-BBBB")          # not counted
    page.goto(f"{site}/manage/")
    expect(page.get_by_test_id("stat-total-customers")).to_contain_text("2")
    expect(page.get_by_test_id("stat-total-categories")).to_contain_text("2")
    expect(page.get_by_test_id("stat-total-products")).to_contain_text(str(len(shop)))
    expect(page.get_by_test_id("stat-total-orders")).to_contain_text("2")
    expect(page.get_by_test_id("stat-total-sales")).to_contain_text("₹2,198")


@pytest.mark.tc("TC-ADM-04")
def test_add_category(page, site, admin):
    page.goto(f"{site}/manage/categories/")
    page.get_by_test_id("add-category").click()
    page.get_by_label("Category name").fill("Garden and Outdoors")
    page.get_by_label("Description").fill("Planters, hoses and outdoor lights.")
    page.get_by_test_id("save-category").click()
    expect(toast(page, "Garden and Outdoors")).to_be_visible()
    expect(page.get_by_test_id("category-row").filter(has_text="Garden and Outdoors")).to_be_visible()
    assert Category.objects.filter(category_name="Garden and Outdoors").exists()


@pytest.mark.tc("TC-ADM-05")
def test_view_categories(page, site, admin):
    make_shop()
    page.goto(f"{site}/manage/categories/")
    rows = page.get_by_test_id("category-row")
    expect(rows).to_have_count(2)
    expect(rows.filter(has_text="Electronics")).to_contain_text("4")
    expect(rows.filter(has_text="Electronics")).to_contain_text("Active")


@pytest.mark.tc("TC-ADM-06")
def test_update_category(page, site, admin):
    category = Category.objects.create(category_name="Garden", description="Old text.")
    page.goto(f"{site}/manage/categories/")
    page.get_by_test_id("category-row").filter(has_text="Garden").get_by_test_id("edit-category").click()
    page.get_by_label("Category name").fill("Garden and Outdoors")
    page.get_by_label("Description").fill("Planters and hoses.")
    page.get_by_test_id("save-category").click()
    expect(toast(page, "updated")).to_be_visible()
    category.refresh_from_db()
    assert category.category_name == "Garden and Outdoors" and category.description == "Planters and hoses."


@pytest.mark.tc("TC-ADM-07")
def test_delete_category(page, site, admin):
    Category.objects.create(category_name="Seasonal")
    page.goto(f"{site}/manage/categories/")
    page.get_by_test_id("category-row").filter(has_text="Seasonal").get_by_test_id("delete-category").click()
    confirm(page)
    expect(toast(page, "deleted")).to_be_visible()
    expect(page.get_by_test_id("category-row").filter(has_text="Seasonal")).to_have_count(0)
    assert not Category.objects.filter(category_name="Seasonal").exists()


@pytest.mark.tc("TC-ADM-08")
def test_add_product(page, site, admin):
    Category.objects.create(category_name="Electronics")
    page.goto(f"{site}/manage/products/")
    page.get_by_test_id("add-product").click()
    page.get_by_label("Category").select_option(label="Electronics")
    page.get_by_label("Product name").fill("Studio Neckband Earphones")
    page.get_by_label("Brand").fill("Sonvale")
    page.get_by_label("Price (₹)").fill("1499")
    page.get_by_label("Quantity in stock").fill("25")
    page.get_by_label("Description").fill("Bluetooth neckband earphones with magnetic earbuds.")
    page.get_by_label("Keywords").fill("earphones, neckband, bluetooth")
    page.get_by_test_id("save-product").click()
    expect(toast(page, "Studio Neckband Earphones")).to_be_visible()
    product = Product.objects.get(product_name="Studio Neckband Earphones")
    assert product.price == 1499 and product.quantity == 25 and product.category.category_name == "Electronics"


@pytest.mark.tc("TC-ADM-09")
def test_view_products(page, site, admin):
    shop = make_shop()
    page.goto(f"{site}/manage/products/")
    expect(page.get_by_test_id("product-row")).to_have_count(len(shop))
    kettle = page.get_by_test_id("product-row").filter(has_text="Electric Kettle")
    expect(kettle).to_contain_text("Kitchen and Home Appliances")
    expect(kettle).to_contain_text("₹1,099.00")
    expect(kettle).to_contain_text("20")


@pytest.mark.tc("TC-ADM-10")
def test_update_product(page, site, admin):
    shop = make_shop()
    page.goto(f"{site}/manage/products/")
    page.get_by_test_id("product-row").filter(has_text="Electric Kettle").get_by_test_id("edit-product").click()
    page.get_by_label("Price (₹)").fill("999")
    page.get_by_label("MRP (₹, optional)").fill("1399")
    page.get_by_label("Quantity in stock").fill("30")
    page.get_by_test_id("save-product").click()
    expect(toast(page, "updated")).to_be_visible()
    kettle = Product.objects.get(pk=shop["Electric Kettle"].pk)
    assert kettle.price == 999 and kettle.quantity == 30


@pytest.mark.tc("TC-ADM-11")
def test_delete_product(page, site, admin):
    shop = make_shop()
    page.goto(f"{site}/manage/products/")
    page.get_by_test_id("product-row").filter(has_text="Hand Blender").get_by_test_id("delete-product").click()
    confirm(page)
    expect(toast(page, "deleted")).to_be_visible()
    assert not Product.objects.filter(pk=shop["Hand Blender"].pk).exists()  # no orders, so it is really deleted


@pytest.mark.tc("TC-ADM-12")
def test_view_customers(page, site, admin):
    make_customer()
    make_customer("Ravi Kumar", "ravi@example.com", "9123456780", "5 MG Road, Kochi 682016")
    page.goto(f"{site}/manage/customers/")
    rows = page.get_by_test_id("customer-row")
    expect(rows).to_have_count(2)
    asha = rows.filter(has_text="Asha Rao")
    expect(asha).to_contain_text("asha@example.com")
    expect(asha).to_contain_text("9876543210")
    expect(asha.get_by_test_id("customer-status")).to_have_text("Active")


@pytest.mark.tc("TC-ADM-13")
def test_activate_customer(page, site, admin):
    customer = make_customer()
    set_customer_status(customer, "Inactive")
    page.goto(f"{site}/manage/customers/")
    page.get_by_test_id("customer-row").filter(has_text="Asha Rao").get_by_test_id("activate-customer").click()
    expect(toast(page, "activated")).to_be_visible()
    customer.refresh_from_db()
    assert customer.status == "Active" and customer.user.is_active


@pytest.mark.tc("TC-ADM-14")
def test_deactivate_customer(page, site, admin):
    customer = make_customer()
    page.goto(f"{site}/manage/customers/")
    page.get_by_test_id("customer-row").filter(has_text="Asha Rao").get_by_test_id("deactivate-customer").click()
    confirm(page)
    expect(toast(page, "deactivated")).to_be_visible()
    expect(page.get_by_test_id("customer-row").filter(has_text="Asha Rao").get_by_test_id("customer-status")).to_have_text("Inactive")
    customer.refresh_from_db()
    assert customer.status == "Inactive"


@pytest.mark.tc("TC-ADM-15")
def test_view_orders(page, site, admin):
    shop = make_shop()
    asha = make_customer()
    make_order(asha, [(shop["Electric Kettle"], 1), (shop["Hand Blender"], 1)], OrderStatus.CONFIRMED, "ORD-20261003-CCCC")
    page.goto(f"{site}/manage/orders/")
    group = page.get_by_test_id("order-group").filter(has_text="ORD-20261003-CCCC")
    expect(group).to_have_count(1)  # two rows, one order
    expect(group).to_contain_text("Asha Rao")
    expect(group).to_contain_text("₹2,398")
    expect(group.get_by_test_id("order-status").first).to_contain_text("Confirmed")


@pytest.mark.tc("TC-ADM-16")
def test_update_order_status(page, site, admin):
    shop = make_shop()
    order_id = make_order(make_customer(), [(shop["Electric Kettle"], 1), (shop["Hand Blender"], 1)], OrderStatus.CONFIRMED)
    page.goto(f"{site}/manage/orders/{order_id}/")
    page.get_by_label("New status").select_option("Shipped")
    page.get_by_test_id("update-status").click()
    expect(toast(page, "now Shipped")).to_be_visible()
    expect(page.get_by_test_id("order-status").first).to_contain_text("Shipped")
    assert set(Order.objects.filter(order_id=order_id).values_list("order_status", flat=True)) == {OrderStatus.SHIPPED}


@pytest.mark.tc("TC-ADM-17")
def test_view_ratings_and_reviews(page, site, admin):
    shop = make_shop()
    asha = make_customer()
    Rating.objects.create(customer=asha, product=shop["Electric Kettle"], rating=5)
    Review.objects.create(customer=asha, product=shop["Electric Kettle"], review="Boils fast and pours cleanly.")
    page.goto(f"{site}/manage/reviews/")
    row = page.get_by_test_id("review-row").filter(has_text="Electric Kettle")
    expect(row).to_contain_text("Asha Rao")
    expect(row).to_contain_text("Boils fast and pours cleanly.")


@pytest.mark.tc("TC-ADM-18")
def test_view_queries(page, site, admin):
    asha = make_customer()
    start_customer_query(asha.user, "Delivery date", "When will my order arrive?")
    page.goto(f"{site}/manage/queries/")
    row = page.get_by_test_id("query-row").filter(has_text="Delivery date")
    expect(row).to_contain_text("Asha Rao")
    expect(row).to_contain_text("1")  # one unread message


@pytest.mark.tc("TC-ADM-19")
def test_post_query(page, site, admin):
    asha = make_customer()
    page.goto(f"{site}/manage/queries/")
    page.get_by_test_id("new-query").click()
    page.get_by_label("Customer").select_option(label="Asha Rao (asha@example.com)")
    page.get_by_label("Subject").fill("Your kettle order")
    page.get_by_label("Message").fill("Your kettle ships today. Reply here with any questions.")
    page.get_by_test_id("send-query").click()
    expect(page.get_by_test_id("thread-subject")).to_have_text("Your kettle order")
    message = Message.objects.get(subject="Your kettle order")
    assert message.parent_message_id is None and message.sender == admin and message.receiver == asha.user
    assert message.sender_type == "admin" and message.receiver_type == "customer"


@pytest.mark.tc("TC-ADM-20")
def test_reply_query(page, site, admin):
    asha = make_customer()
    first = start_customer_query(asha.user, "Delivery date", "When will my order arrive?")
    page.goto(f"{site}/manage/queries/{first.conversation_id}/")
    page.get_by_label("Your reply").fill("It ships tomorrow morning.")
    page.get_by_test_id("send-reply").click()
    expect(toast(page, "Reply sent")).to_be_visible()
    answer = Message.objects.get(message="It ships tomorrow morning.")
    assert answer.conversation_id == first.conversation_id and answer.parent_message == first
    assert answer.receiver == asha.user


@pytest.mark.tc("TC-ADM-21")
def test_view_conversation_history(page, site, admin):
    asha = make_customer()
    first = start_customer_query(asha.user, "Delivery date", "When will my order arrive?")
    reply(first.conversation_id, admin, "It ships tomorrow.")
    reply(first.conversation_id, asha.user, "Thanks!")
    page.goto(f"{site}/manage/queries/")
    page.get_by_test_id("query-row").filter(has_text="Delivery date").click()
    messages = page.get_by_test_id("thread-message")
    expect(messages).to_have_count(3)
    expect(messages.nth(0)).to_contain_text("When will my order arrive?")
    expect(messages.nth(2)).to_contain_text("Thanks!")


@pytest.mark.tc("TC-ADM-22")
def test_admin_logout(page, site, admin):
    page.goto(f"{site}/manage/")
    page.get_by_test_id("admin-logout").click()
    expect(toast(page, "signed out")).to_be_visible()
    page.goto(f"{site}/manage/products/")
    expect(page).to_have_url(re.compile(r"/manage/login/"))
