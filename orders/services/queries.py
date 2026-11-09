"""Read-only order helpers shared by the admin panel and the customer's order history."""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal

from django.db.models import Count, Max, Min, Q, QuerySet, Sum

from orders.models import Order, OrderStatus, Payment


@dataclass
class OrderGroup:
    """All rows that share one order_id, summarised."""

    order_id: str
    customer_id: int
    customer_name: str
    order_date: datetime
    status: str
    item_count: int
    quantity: int
    total: Decimal
    paid: bool
    rows: list = field(default_factory=list)


def paid_order_ids(order_ids=None) -> set[str]:
    qs = Payment.objects.filter(payment_status=Payment.Status.SUCCESS)
    if order_ids is not None:
        qs = qs.filter(order_id__in=order_ids)
    return set(qs.values_list("order_id", flat=True))


def order_groups(rows: QuerySet[Order], with_rows: bool = False) -> list[OrderGroup]:
    """Summarise order rows into one entry per order_id, newest first."""
    summary = (rows.values("order_id", "customer_id", "customer__name")
               .annotate(order_date=Min("order_date"), status=Max("order_status"), item_count=Count("id"),
                         quantity=Sum("quantity"), total=Sum("amount"))
               .order_by("-order_date"))
    ids = [s["order_id"] for s in summary]
    paid = paid_order_ids(ids)
    by_id = {}
    if with_rows:
        for row in Order.objects.filter(order_id__in=ids).select_related("product").order_by("id"):
            by_id.setdefault(row.order_id, []).append(row)
    return [OrderGroup(order_id=s["order_id"], customer_id=s["customer_id"], customer_name=s["customer__name"],
                       order_date=s["order_date"], status=s["status"], item_count=s["item_count"],
                       quantity=s["quantity"], total=s["total"] or Decimal("0"), paid=s["order_id"] in paid,
                       rows=by_id.get(s["order_id"], []))
            for s in summary]


def sales_rows() -> QuerySet[Order]:
    """Order rows that count as sales: paid and not cancelled."""
    return Order.objects.filter(order_id__in=paid_order_ids()).exclude(order_status=OrderStatus.CANCELLED)


def total_sales() -> Decimal:
    return sales_rows().aggregate(total=Sum("amount"))["total"] or Decimal("0")


def status_counts() -> dict[str, int]:
    """Number of orders (distinct order_id) per status."""
    counts = {s: 0 for s in OrderStatus.values}
    for row in Order.objects.values("order_status").annotate(n=Count("order_id", distinct=True)):
        counts[row["order_status"]] = row["n"]
    return counts


def search_filter(text: str) -> Q:
    return Q(order_id__icontains=text) | Q(customer__name__icontains=text) | Q(customer__email__icontains=text) | Q(product_name__icontains=text)
