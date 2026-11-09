"""Dummy payment (brief rule 5). No real gateway: the customer chooses whether the payment
succeeds or fails, so both paths can be shown.

Success → a Payment row (Success), every row of the order becomes Confirmed, the cart items are
cleared, `purchase` interactions are logged and the order email is sent after the commit.
Failure → a Payment row (Failed) only; the order stays Pending and can be paid again.
Paying an order that is already paid creates nothing new (and the database refuses a second
successful payment for the same order).
"""

import secrets
from dataclasses import dataclass

from django.db import IntegrityError, transaction
from django.utils import timezone

from orders.emails import send_order_email
from orders.models import CartItem, Order, OrderStatus, Payment
from orders.services.checkout import CheckoutError, order_total
from recommender.interactions import PURCHASE, log_interaction

SUCCESS = "success"
FAILURE = "failure"


@dataclass
class PaymentResult:
    payment: Payment | None
    succeeded: bool
    already_paid: bool = False


def new_reference() -> str:
    return f"PAY-{secrets.token_hex(5).upper()}"


def pay(customer, order_id: str, method: str, outcome: str) -> PaymentResult:
    """Brief: Dummy Payment (order_id, customer_id, total_amount, payment_method, payment_status, payment_date)."""
    if method not in Payment.Method.values:
        raise CheckoutError("Choose a payment method.")
    if outcome not in (SUCCESS, FAILURE):
        raise CheckoutError("Choose whether the payment should succeed or fail.")
    try:
        with transaction.atomic():
            rows = list(Order.objects.select_for_update().filter(order_id=order_id, customer=customer).select_related("product"))
            if not rows:
                raise CheckoutError("We couldn't find that order.")
            existing = Payment.objects.filter(order_id=order_id, payment_status=Payment.Status.SUCCESS).first()
            if existing:
                return PaymentResult(payment=existing, succeeded=True, already_paid=True)
            if rows[0].order_status == OrderStatus.CANCELLED:
                raise CheckoutError("This order was cancelled, so it can't be paid. Please check out again.")
            status = Payment.Status.SUCCESS if outcome == SUCCESS else Payment.Status.FAILED
            payment = Payment.objects.create(order_id=order_id, customer=customer, total_amount=order_total(order_id),
                                             payment_method=method, payment_status=status, payment_date=timezone.now(),
                                             reference=new_reference())
            if status == Payment.Status.FAILED:
                return PaymentResult(payment=payment, succeeded=False)
            Order.objects.filter(order_id=order_id).update(order_status=OrderStatus.CONFIRMED, updated_at=timezone.now())
            CartItem.objects.filter(customer=customer, product_id__in=[r.product_id for r in rows]).delete()
            for row in rows:
                log_interaction(customer, row.product, PURCHASE)
            transaction.on_commit(lambda: send_order_email(order_id))
            return PaymentResult(payment=payment, succeeded=True)
    except IntegrityError:
        # A second request raced this one and recorded the successful payment first.
        existing = Payment.objects.get(order_id=order_id, payment_status=Payment.Status.SUCCESS)
        return PaymentResult(payment=existing, succeeded=True, already_paid=True)
