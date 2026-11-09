"""Ratings and reviews (brief: Add Rating, Add Review).

Only a customer who bought the product may rate or review it. "Bought" means an
order row for the product whose payment went through: Confirmed, Shipped or
Delivered (a Pending or Cancelled order does not count). Each customer has at most
one rating and one review per product; saving again updates them.
"""

from dataclasses import dataclass

from django.db import transaction
from django.utils import timezone

from accounts.models import Customer
from catalog.models import Product
from orders.models import Order, OrderStatus
from reviews.models import Rating, Review

PURCHASED_STATUSES = (OrderStatus.CONFIRMED, OrderStatus.SHIPPED, OrderStatus.DELIVERED)
NOT_A_BUYER_MESSAGE = "Only customers who bought this product can rate or review it."


class ReviewError(Exception):
    """Raised when a rating or review can't be saved; the message is shown to the customer."""


def can_review(customer: Customer | None, product: Product) -> bool:
    """True when the customer has a paid (Confirmed / Shipped / Delivered) order for the product."""
    if customer is None:
        return False
    return Order.objects.filter(customer=customer, product=product, order_status__in=PURCHASED_STATUSES).exists()


def _ensure_buyer(customer: Customer, product: Product) -> None:
    if not can_review(customer, product):
        raise ReviewError(NOT_A_BUYER_MESSAGE)


@transaction.atomic
def save_rating(customer: Customer, product: Product, value: int) -> tuple[Rating, bool]:
    """Add or update the customer's 1–5 rating. Returns (rating, created)."""
    _ensure_buyer(customer, product)
    if value not in range(1, 6):
        raise ReviewError("Choose a rating from 1 to 5 stars.")
    return Rating.objects.update_or_create(
        customer=customer, product=product, defaults={"rating": value, "posted_date": timezone.now()},
    )


@transaction.atomic
def save_review(customer: Customer, product: Product, text: str) -> tuple[Review, bool]:
    """Add or update the customer's written review. Returns (review, created)."""
    _ensure_buyer(customer, product)
    text = text.strip()
    if len(text) < 10:
        raise ReviewError("Write at least 10 characters so the review helps other shoppers.")
    return Review.objects.update_or_create(
        customer=customer, product=product, defaults={"review": text, "posted_date": timezone.now()},
    )


@dataclass
class MyFeedback:
    """What the product page needs to show the signed-in customer's own rating and review."""

    can_review: bool
    rating: Rating | None
    review: Review | None


def my_feedback(customer: Customer | None, product: Product) -> MyFeedback:
    if customer is None:
        return MyFeedback(False, None, None)
    return MyFeedback(
        can_review=can_review(customer, product),
        rating=Rating.objects.filter(customer=customer, product=product).first(),
        review=Review.objects.filter(customer=customer, product=product).first(),
    )
