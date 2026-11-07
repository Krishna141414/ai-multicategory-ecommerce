"""Cart, orders and dummy payments.

Brief fields:
- Add to Cart: id, customer_id, product_id, quantity, added_date
- Submit Cart (orders): id, order_id, product_id, customer_id, quantity, price, amount, order_date, order_status
- Dummy Payment: id, order_id, customer_id, total_amount, payment_method, payment_status, payment_date
"""

from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone

from accounts.models import Customer
from catalog.models import Product


class CartItem(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="cart_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="cart_items")
    quantity = models.PositiveIntegerField(default=1)
    added_date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["added_date"]
        constraints = [
            models.UniqueConstraint(fields=["customer", "product"], name="one_cart_row_per_product"),
            models.CheckConstraint(condition=Q(quantity__gte=1), name="cart_quantity_gte_1"),
        ]

    def __str__(self) -> str:
        return f"{self.quantity} × {self.product}"

    @property
    def line_total(self):
        return self.product.price * self.quantity


class OrderStatus(models.TextChoices):
    PENDING = "Pending", "Pending"
    CONFIRMED = "Confirmed", "Confirmed"
    SHIPPED = "Shipped", "Shipped"
    DELIVERED = "Delivered", "Delivered"
    CANCELLED = "Cancelled", "Cancelled"


class Order(models.Model):
    """One row per product in a checkout; rows of one checkout share `order_id`.

    `product_name` and `price` are snapshots so history stays correct even if the
    product is later edited or removed from listings.
    """

    order_id = models.CharField(max_length=24, db_index=True)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="orders")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="orders")
    product_name = models.CharField(max_length=160)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    order_date = models.DateTimeField(default=timezone.now)
    order_status = models.CharField(max_length=10, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    checkout_key = models.CharField(max_length=64, blank=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-order_date", "id"]
        constraints = [
            models.CheckConstraint(condition=Q(quantity__gte=1), name="order_quantity_gte_1"),
            models.CheckConstraint(condition=Q(price__gt=0), name="order_price_gt_0"),
        ]

    def __str__(self) -> str:
        return f"{self.order_id} · {self.product_name}"

    def save(self, *args, **kwargs):
        self.amount = self.price * self.quantity
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        return reverse("orders:detail", args=[self.order_id])


class Payment(models.Model):
    class Method(models.TextChoices):
        CARD = "Card", "Credit / debit card"
        UPI = "UPI", "UPI"
        NET_BANKING = "Net Banking", "Net banking"

    class Status(models.TextChoices):
        SUCCESS = "Success", "Success"
        FAILED = "Failed", "Failed"

    order_id = models.CharField(max_length=24, db_index=True)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="payments")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=Method.choices)
    payment_status = models.CharField(max_length=10, choices=Status.choices)
    payment_date = models.DateTimeField(default=timezone.now)
    reference = models.CharField(max_length=24, unique=True)

    class Meta:
        ordering = ["-payment_date"]
        constraints = [
            # At most one successful payment per order: the database itself refuses a double charge.
            models.UniqueConstraint(fields=["order_id"], condition=Q(payment_status="Success"), name="one_success_per_order"),
        ]

    def __str__(self) -> str:
        return f"{self.reference} {self.order_id} {self.payment_status}"
