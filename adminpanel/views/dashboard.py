"""Admin dashboard: the brief's five totals, orders by status, recent orders and a 14-day chart."""

from django.shortcuts import render

from adminpanel.services import daily_series, dashboard_stats, recent_orders
from core.permissions import admin_required


@admin_required
def dashboard(request):
    series = daily_series(14)
    return render(request, "adminpanel/dashboard.html", {
        "section": "dashboard",
        "stats": dashboard_stats(),
        "recent": recent_orders(6),
        "series": series,
        "series_orders": sum(d["orders"] for d in series),
        "series_sales": sum(d["sales"] for d in series),
    })
