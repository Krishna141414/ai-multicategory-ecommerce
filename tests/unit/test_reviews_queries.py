"""Phase 7: ratings and reviews (buyers only, editable) and customer queries (own threads only)."""

from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from accounts.services import register_customer
from catalog.models import Category, Product
from messaging.models import Message
from orders.models import Order, OrderStatus
from reviews import services
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
def other_customer():
    return register_customer(name="Ravi Kumar", email="ravi@example.com", password=PASSWORD,
                             mobile_number="9123456780", address="5 MG Road, Kochi 682016")


@pytest.fixture
def product():
    category = Category.objects.create(category_name="Electronics")
    return Product.objects.create(category=category, product_name="Arc 3 Wireless Earbuds", brand="Sonvale",
                                  price=Decimal("2499.00"), description="Earbuds.", quantity=10)


def buy(customer, product, status=OrderStatus.DELIVERED):
    return Order.objects.create(order_id=f"ORD-T-{customer.pk}{status[:3]}", customer=customer, product=product,
                                product_name=product.product_name, quantity=1, price=product.price, order_status=status)


def sign_in(client, customer):
    client.force_login(customer.user, backend="accounts.backends.EmailBackend")
    return client


# ---------- ratings and reviews ----------

def test_cannot_review_without_purchase(customer, product):
    assert services.can_review(customer, product) is False
    with pytest.raises(services.ReviewError):
        services.save_rating(customer, product, 5)
    with pytest.raises(services.ReviewError):
        services.save_review(customer, product, "Great sound for the price.")
    assert not Rating.objects.exists() and not Review.objects.exists()


@pytest.mark.parametrize("status, allowed", [
    (OrderStatus.PENDING, False), (OrderStatus.CANCELLED, False),
    (OrderStatus.CONFIRMED, True), (OrderStatus.SHIPPED, True), (OrderStatus.DELIVERED, True),
])
def test_only_paid_orders_count_as_a_purchase(customer, product, status, allowed):
    buy(customer, product, status)
    assert services.can_review(customer, product) is allowed


def test_rating_is_updated_not_duplicated(customer, product):
    buy(customer, product)
    _, created = services.save_rating(customer, product, 3)
    rating, created_again = services.save_rating(customer, product, 5)
    assert created and not created_again
    assert Rating.objects.count() == 1 and rating.rating == 5


def test_review_is_updated_not_duplicated(customer, product):
    buy(customer, product)
    services.save_review(customer, product, "Good fit, the case feels a bit light.")
    review, created = services.save_review(customer, product, "  Two weeks in: battery still lasts all day.  ")
    assert not created and Review.objects.count() == 1
    assert review.review == "Two weeks in: battery still lasts all day."


@pytest.mark.parametrize("value", [0, 6])
def test_rating_out_of_range_is_rejected(customer, product, value):
    buy(customer, product)
    with pytest.raises(services.ReviewError):
        services.save_rating(customer, product, value)


def test_rate_and_review_views(client, customer, product):
    sign_in(client, customer)
    # not a buyer yet: rejected with a message, nothing saved
    client.post(reverse("reviews:rate", args=[product.pk]), {"rating": 4})
    assert not Rating.objects.exists()
    buy(customer, product)
    response = client.post(reverse("reviews:rate", args=[product.pk]), {"rating": 4})
    assert response["Location"].endswith("#your-feedback")
    client.post(reverse("reviews:review", args=[product.pk]), {"review": "Comfortable for long calls."})
    assert Rating.objects.get().rating == 4 and Review.objects.get().review == "Comfortable for long calls."
    page = client.get(product.get_absolute_url()).content.decode()
    assert "4.0 out of 5" in page and "Comfortable for long calls." in page and "Update review" in page
    # invalid input is rejected server-side
    client.post(reverse("reviews:rate", args=[product.pk]), {"rating": 9})
    client.post(reverse("reviews:review", args=[product.pk]), {"review": "short"})
    assert Rating.objects.get().rating == 4 and Review.objects.get().review == "Comfortable for long calls."


def test_rate_requires_customer_login(client, product):
    response = client.post(reverse("reviews:rate", args=[product.pk]), {"rating": 5})
    assert reverse("accounts:login") in response["Location"] and not Rating.objects.exists()


def test_product_page_hides_form_from_non_buyers(client, customer, product):
    page = sign_in(client, customer).get(product.get_absolute_url()).content.decode()
    assert 'data-testid="review-not-allowed"' in page and 'data-testid="rating-form"' not in page


# ---------- customer queries ----------

def test_post_query_starts_a_conversation(client, admin_user, customer):
    sign_in(client, customer)
    response = client.post(reverse("messaging:new"), {"subject": "Delivery date", "message": "When will my order arrive?"})
    message = Message.objects.get()
    assert response["Location"] == reverse("messaging:thread", args=[message.conversation_id])
    assert message.parent_message is None and message.sender == customer.user and message.receiver == admin_user
    assert message.sender_type == "customer" and message.receiver_type == "admin"


def test_query_form_validates(client, admin_user, customer):
    response = sign_in(client, customer).post(reverse("messaging:new"), {"subject": "", "message": "hi"})
    assert response.status_code == 200 and not Message.objects.exists()


def test_reply_reuses_conversation_id_and_points_to_parent(client, admin_user, customer):
    sign_in(client, customer)
    client.post(reverse("messaging:new"), {"subject": "Size exchange", "message": "Can I swap the kurta for an L?"})
    first = Message.objects.get()
    client.post(reverse("messaging:thread", args=[first.conversation_id]), {"message": "Order ORD-1, thanks."})
    reply = Message.objects.exclude(pk=first.pk).get()
    assert reply.conversation_id == first.conversation_id and reply.parent_message == first
    assert reply.receiver == admin_user


def test_customer_sees_only_own_conversations(client, admin_user, customer, other_customer):
    sign_in(client, other_customer)
    client.post(reverse("messaging:new"), {"subject": "Ravi's question", "message": "Is the trimmer waterproof?"})
    ravi_thread = Message.objects.get().conversation_id
    client.logout()
    sign_in(client, customer)
    listing = client.get(reverse("messaging:list")).content.decode()
    assert "Ravi&#x27;s question" not in listing and "Ravi's question" not in listing
    assert client.get(reverse("messaging:thread", args=[ravi_thread])).status_code == 403
    assert client.post(reverse("messaging:thread", args=[ravi_thread]), {"message": "Sneaky reply"}).status_code == 403
    assert Message.objects.count() == 1


def test_admin_reply_shows_in_customer_thread_and_marks_read(client, admin_user, customer):
    from messaging.services import reply, start_customer_query

    first = start_customer_query(customer.user, "Warranty", "Does the kettle have a warranty?")
    reply(first.conversation_id, admin_user, "Yes, one year from delivery.")
    sign_in(client, customer)
    listing = client.get(reverse("messaging:list")).content.decode()
    assert "1 new" in listing
    page = client.get(reverse("messaging:thread", args=[first.conversation_id])).content.decode()
    assert "Yes, one year from delivery." in page
    assert not Message.objects.filter(receiver=customer.user, status=Message.Status.UNREAD).exists()


def test_queries_require_login(client):
    assert reverse("accounts:login") in client.get(reverse("messaging:list"))["Location"]
