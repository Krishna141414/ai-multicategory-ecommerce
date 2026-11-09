"""Brief: View Orders (grouped by order_id) and Update Order Status."""

from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from adminpanel.forms import OrderStatusForm
from adminpanel.views.common import paginate, query_without_page
from core.permissions import admin_required
from orders.models import Order, OrderStatus, Payment
from orders.services.queries import order_groups, search_filter, status_counts
from orders.services.status import OrderStatusError, set_order_status


@admin_required
def order_list(request):
    q = request.GET.get("q", "").strip()
    status = request.GET.get("status", "")
    rows = Order.objects.all()
    if q:
        rows = rows.filter(search_filter(q))
    if status in OrderStatus.values:
        rows = rows.filter(order_status=status)
    groups = order_groups(rows, with_rows=True)
    return render(request, "adminpanel/orders/list.html", {
        "section": "orders", "page": paginate(request, groups), "q": q, "status": status,
        "statuses": OrderStatus.values, "counts": status_counts(), "qs": query_without_page(request),
    })


@admin_required
def order_detail(request, order_id):
    rows = list(Order.objects.filter(order_id=order_id).select_related("product", "customer").order_by("id"))
    if not rows:
        raise Http404("Order not found")
    current = rows[0].order_status
    return render(request, "adminpanel/orders/detail.html", {
        "section": "orders", "order_id": order_id, "rows": rows, "customer": rows[0].customer,
        "status": current, "total": sum(r.amount for r in rows),
        "payments": Payment.objects.filter(order_id=order_id).order_by("-payment_date"),
        "form": OrderStatusForm(current_status=current),
    })


@admin_required
@require_POST
def order_update_status(request, order_id):
    rows = Order.objects.filter(order_id=order_id)
    if not rows.exists():
        raise Http404("Order not found")
    form = OrderStatusForm(request.POST, current_status=rows.first().order_status)
    if form.is_valid():
        new_status = form.cleaned_data["order_status"]
        try:
            set_order_status(order_id, new_status)
        except OrderStatusError as exc:
            messages.error(request, str(exc))
        else:
            note = " Stock for its items was put back." if new_status == OrderStatus.CANCELLED else ""
            messages.success(request, f"Order {order_id} is now {new_status}.{note}")
    else:
        messages.error(request, "That status change isn’t allowed for this order.")
    return redirect("adminpanel:order_detail", order_id=order_id)
