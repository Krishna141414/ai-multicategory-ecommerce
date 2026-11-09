"""Numbers for the admin dashboard (brief: total_customers, total_categories, total_products,
total_orders, total_sales)."""

from datetime import timedelta
from decimal import Decimal

from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone

from accounts.models import Customer
from catalog.models import Category, Product
from orders.models import Order
from orders.services.queries import order_groups, sales_rows, status_counts, total_sales


def dashboard_stats() -> dict:
    return {
        "total_customers": Customer.objects.count(),
        "total_categories": Category.objects.count(),
        "total_products": Product.objects.count(),
        "total_orders": Order.objects.values("order_id").distinct().count(),
        "total_sales": total_sales(),
        "active_products": Product.objects.active().count(),
        "out_of_stock": Product.objects.active().filter(quantity=0).count(),
        "status_counts": status_counts(),
    }


def daily_series(days: int = 14) -> list[dict]:
    """Orders placed and paid sales per day for the last `days` days (oldest first)."""
    today = timezone.localdate()
    start = today - timedelta(days=days - 1)
    orders = {r["day"]: r["n"] for r in Order.objects.filter(order_date__date__gte=start)
              .annotate(day=TruncDate("order_date")).values("day").annotate(n=Count("order_id", distinct=True))}
    sales = {r["day"]: r["total"] for r in sales_rows().filter(order_date__date__gte=start)
             .annotate(day=TruncDate("order_date")).values("day").annotate(total=Sum("amount"))}
    series = []
    peak = max([float(v) for v in sales.values()] + [1.0])
    for i in range(days):
        day = start + timedelta(days=i)
        amount = sales.get(day) or Decimal("0")
        series.append({"day": day, "orders": orders.get(day, 0), "sales": amount, "height": round(float(amount) / peak * 100, 1)})
    return series


def recent_orders(limit: int = 6):
    return order_groups(Order.objects.all())[:limit]
