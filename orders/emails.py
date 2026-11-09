"""Order confirmation email (brief: Order Information Email).

By default Django's file email backend writes each message to sent_emails/, so this works
offline; set EMAIL_MODE=smtp in .env to send real mail.
"""

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from orders.models import Order


def send_order_email(order_id: str) -> None:
    """Email the order id, items, quantities, amounts, total and status to the customer."""
    rows = list(Order.objects.filter(order_id=order_id).select_related("customer").order_by("id"))
    if not rows:
        return
    customer = rows[0].customer
    context = {
        "store": settings.STORE_NAME, "order_id": order_id, "customer": customer, "rows": rows,
        "total": sum(r.amount for r in rows), "status": rows[0].order_status, "order_date": rows[0].order_date,
    }
    subject = f"{settings.STORE_NAME} order {order_id} is {rows[0].order_status.lower()}"
    text = render_to_string("emails/order_confirmation.txt", context)
    html = render_to_string("emails/order_confirmation.html", context)
    message = EmailMultiAlternatives(subject, text, settings.DEFAULT_FROM_EMAIL, [customer.email])
    message.attach_alternative(html, "text/html")
    message.send()
