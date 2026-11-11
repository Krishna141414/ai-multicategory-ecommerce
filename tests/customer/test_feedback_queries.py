"""Customer ratings, reviews and queries (TC-CUS-21 to 26)."""

import pytest
from playwright.sync_api import expect

from messaging.models import Message
from messaging.services import reply, start_customer_query
from orders.models import OrderStatus
from reviews.models import Rating, Review
from tests.factories import make_admin, make_customer, make_order, make_shop
from tests.pages import ProductPage

pytestmark = [pytest.mark.customer, pytest.mark.django_db(transaction=True)]


@pytest.fixture
def buyer(as_customer):
    """A signed-in customer who has received the Electric Kettle."""
    shop = make_shop()
    customer = make_customer()
    make_order(customer, [(shop["Electric Kettle"], 1)], OrderStatus.DELIVERED)
    as_customer(customer)
    return customer, shop["Electric Kettle"]


@pytest.mark.tc("TC-CUS-21")
def test_add_rating(page, site, buyer):
    customer, kettle = buyer
    ProductPage(page, site).open_product(kettle)
    page.get_by_test_id("star-4").click()
    page.get_by_test_id("save-rating").click()
    expect(page.get_by_test_id("toast").filter(has_text="rating is saved")).to_be_visible()
    expect(page.get_by_test_id("product-rating")).to_contain_text("4.0 out of 5")
    assert Rating.objects.get(customer=customer, product=kettle).rating == 4


@pytest.mark.tc("TC-CUS-22")
def test_add_review(page, site, buyer):
    customer, kettle = buyer
    ProductPage(page, site).open_product(kettle)
    page.get_by_label("Your review").fill("Boils a full litre in about three minutes. The lid clicks shut firmly.")
    page.get_by_test_id("post-review").click()
    expect(page.get_by_test_id("toast").filter(has_text="review is posted")).to_be_visible()
    expect(page.get_by_test_id("review").filter(has_text="three minutes")).to_be_visible()
    assert "three minutes" in Review.objects.get(customer=customer, product=kettle).review


@pytest.fixture
def queries_customer(as_customer):
    admin = make_admin()  # receives customer queries
    customer = make_customer()
    as_customer(customer)
    return admin, customer


@pytest.mark.tc("TC-CUS-23")
def test_post_query(page, site, queries_customer):
    _, customer = queries_customer
    page.goto(f"{site}/queries/")
    page.get_by_test_id("new-query").click()
    page.get_by_label("Subject").fill("Kettle warranty")
    page.get_by_label("Message").fill("How long is the warranty on the electric kettle?")
    page.get_by_test_id("send-query").click()
    expect(page.get_by_test_id("thread-subject")).to_have_text("Kettle warranty")
    message = Message.objects.get(sender=customer.user)
    assert message.parent_message_id is None and message.conversation_id.startswith("CNV-")
    assert message.sender_type == "customer" and message.receiver_type == "admin"


@pytest.mark.tc("TC-CUS-24")
def test_view_queries(page, site, queries_customer):
    _, customer = queries_customer
    other = make_customer("Ravi Kumar", "ravi@example.com", "9123456780", "5 MG Road, Kochi 682016")
    start_customer_query(customer.user, "Delivery date", "When will my order arrive?")
    start_customer_query(customer.user, "Size exchange", "Can I swap the size?")
    start_customer_query(other.user, "Ravi's private question", "Is this waterproof?")
    page.goto(f"{site}/queries/")
    rows = page.get_by_test_id("query-row")
    expect(rows).to_have_count(2)
    expect(page.get_by_test_id("query-list")).not_to_contain_text("Ravi's private question")


@pytest.mark.tc("TC-CUS-25")
def test_reply_query(page, site, queries_customer):
    admin, customer = queries_customer
    first = start_customer_query(customer.user, "Delivery date", "When will my order arrive?")
    reply(first.conversation_id, admin, "It ships tomorrow.")
    page.goto(f"{site}/queries/{first.conversation_id}/")
    page.get_by_label("Your reply").fill("Thank you, I'll be home.")
    page.get_by_test_id("send-reply").click()
    expect(page.get_by_test_id("thread-message")).to_have_count(3)
    latest = Message.objects.filter(conversation_id=first.conversation_id).order_by("-id").first()
    assert latest.sender == customer.user and latest.parent_message.message == "It ships tomorrow."


@pytest.mark.tc("TC-CUS-26")
def test_view_conversation_history(page, site, queries_customer):
    admin, customer = queries_customer
    first = start_customer_query(customer.user, "Delivery date", "When will my order arrive?")
    reply(first.conversation_id, admin, "It ships tomorrow.")
    reply(first.conversation_id, customer.user, "Great, thanks.")
    page.goto(f"{site}/queries/")
    page.get_by_test_id("query-link").filter(has_text="Delivery date").click()
    messages = page.get_by_test_id("thread-message")
    expect(messages).to_have_count(3)
    expect(messages.nth(0)).to_contain_text("When will my order arrive?")
    expect(messages.nth(1)).to_contain_text("It ships tomorrow.")
    expect(messages.nth(1)).to_contain_text("Velora support")
    expect(messages.nth(2)).to_contain_text("Great, thanks.")
