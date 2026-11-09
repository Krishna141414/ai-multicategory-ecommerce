"""Order status changes made by the admin (brief: Update Order Status)."""

from django.db import transaction
from django.db.models import F
from django.utils import timezone

from catalog.models import Product
from orders.models import Order, OrderStatus

# Which status may follow which. Delivered and Cancelled are final.
ALLOWED_TRANSITIONS = {
    OrderStatus.PENDING: {OrderStatus.CONFIRMED, OrderStatus.CANCELLED},
    OrderStatus.CONFIRMED: {OrderStatus.SHIPPED, OrderStatus.CANCELLED},
    OrderStatus.SHIPPED: {OrderStatus.DELIVERED},
    OrderStatus.DELIVERED: set(),
    OrderStatus.CANCELLED: set(),
}


class OrderStatusError(Exception):
    """Raised for a status change that isn't allowed."""


def group_status(order_id: str) -> str:
    """The status of an order group (all rows of one order_id share a status)."""
    row = Order.objects.filter(order_id=order_id).order_by("id").first()
    if row is None:
        raise Order.DoesNotExist(order_id)
    return row.order_status


def next_statuses(current: str) -> list[str]:
    """Statuses the admin may choose next, in the brief's order."""
    allowed = ALLOWED_TRANSITIONS.get(current, set())
    return [s for s in OrderStatus.values if s in allowed]


@transaction.atomic
def set_order_status(order_id: str, new_status: str) -> int:
    """Move every row of an order to `new_status`. Cancelling puts the stock back.

    Returns the number of rows changed. Raises OrderStatusError for a move that isn't allowed.
    """
    rows = list(Order.objects.select_for_update().filter(order_id=order_id))
    if not rows:
        raise OrderStatusError(f"Order {order_id} was not found.")
    current = rows[0].order_status
    if new_status not in OrderStatus.values:
        raise OrderStatusError(f"“{new_status}” is not an order status.")
    if new_status == current:
        return 0
    if new_status not in ALLOWED_TRANSITIONS[current]:
        raise OrderStatusError(f"An order that is {current} can't be moved to {new_status}.")
    if new_status == OrderStatus.CANCELLED:
        for row in rows:  # stock was reserved when the cart was submitted: give it back
            Product.objects.filter(pk=row.product_id).update(quantity=F("quantity") + row.quantity)
    return Order.objects.filter(order_id=order_id).update(order_status=new_status, updated_at=timezone.now())
