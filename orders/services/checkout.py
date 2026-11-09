"""Submit Cart (brief rule 4): one database transaction that re-checks stock, reserves it and
creates one order row per cart item, all sharing one order_id, each with its own id.

Why it is safe on SQLite: the default connection uses transaction_mode=IMMEDIATE, so this
atomic block takes the write lock at BEGIN (select_for_update is a no-op on SQLite, kept for
other databases). Stock is decremented with a conditional UPDATE (quantity >= ordered), so even
two checkouts at once can never oversell; if any line fails, the whole transaction rolls back.
"""

import secrets
from decimal import Decimal

from django.db import transaction
from django.db.models import F, Sum
from django.utils import timezone

from catalog.models import Product
from orders.models import CartItem, Order, OrderStatus, Payment

ORDER_ID_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # no 0/O/1/I to avoid misreading


class CheckoutError(Exception):
    """The cart can't be submitted; the message tells the customer what to fix."""


def new_order_id() -> str:
    """A readable, unique id such as ORD-20261109-7K3Q."""
    today = timezone.localdate().strftime("%Y%m%d")
    while True:
        code = "".join(secrets.choice(ORDER_ID_ALPHABET) for _ in range(4))
        candidate = f"ORD-{today}-{code}"
        if not Order.objects.filter(order_id=candidate).exists():
            return candidate


def order_rows(order_id: str):
    return Order.objects.filter(order_id=order_id).select_related("product").order_by("id")


def order_total(order_id: str) -> Decimal:
    """Total order amount = sum of every row's amount (price × quantity)."""
    return Order.objects.filter(order_id=order_id).aggregate(total=Sum("amount"))["total"] or Decimal("0")


def is_paid(order_id: str) -> bool:
    return Payment.objects.filter(order_id=order_id, payment_status=Payment.Status.SUCCESS).exists()


def _release_unpaid_orders(customer) -> list[str]:
    """Cancel this customer's earlier checkouts that were never paid, putting their stock back.

    A customer who goes back, changes the cart and checks out again should not hold stock twice.
    """
    paid = set(Payment.objects.filter(customer=customer, payment_status=Payment.Status.SUCCESS).values_list("order_id", flat=True))
    stale = (Order.objects.select_for_update().filter(customer=customer, order_status=OrderStatus.PENDING)
             .exclude(order_id__in=paid))
    released = set()
    for row in stale:
        Product.objects.filter(pk=row.product_id).update(quantity=F("quantity") + row.quantity)
        released.add(row.order_id)
    if released:
        Order.objects.filter(order_id__in=released).update(order_status=OrderStatus.CANCELLED, updated_at=timezone.now())
    return sorted(released)


@transaction.atomic
def submit_cart(customer, checkout_key: str) -> str:
    """Brief: Submit Cart. Returns the order_id.

    - Re-submitting the same checkout (double click, browser refresh) returns the same order_id
      instead of creating new rows (checkout_key).
    - Stock is checked and reserved inside this transaction; any problem rolls everything back.
    - The cart is NOT cleared here. It is cleared after a successful payment.
    """
    if not checkout_key:
        raise CheckoutError("Your checkout session expired. Please review your order again.")
    existing = Order.objects.filter(customer=customer, checkout_key=checkout_key).values_list("order_id", flat=True).first()
    if existing:
        return existing

    items = list(CartItem.objects.filter(customer=customer).order_by("id"))
    if not items:
        raise CheckoutError("Your cart is empty.")

    _release_unpaid_orders(customer)

    # Lock the products and read fresh stock (after any release above).
    products = {p.pk: p for p in Product.objects.select_for_update().select_related("category")
                .filter(pk__in=[i.product_id for i in items])}
    problems = []
    for item in items:
        product = products.get(item.product_id)
        if product is None or not product.is_active:
            problems.append("An item in your cart is no longer sold. Remove it and try again.")
        elif item.quantity > product.quantity:
            left = f"only {product.quantity} left" if product.quantity else "now out of stock"
            problems.append(f"“{product.product_name}”: {left}.")
    if problems:
        raise CheckoutError(" ".join(problems))

    order_id = new_order_id()
    now = timezone.now()
    for item in items:
        product = products[item.product_id]
        reserved = Product.objects.filter(pk=product.pk, quantity__gte=item.quantity).update(
            quantity=F("quantity") - item.quantity, updated_at=now)
        if reserved != 1:  # someone bought it a moment ago: undo the whole checkout
            raise CheckoutError(f"“{product.product_name}” just sold out. Your cart was not submitted.")
        Order.objects.create(order_id=order_id, customer=customer, product=product, product_name=product.product_name,
                             quantity=item.quantity, price=product.price, order_date=now,
                             order_status=OrderStatus.PENDING, checkout_key=checkout_key)
    return order_id
