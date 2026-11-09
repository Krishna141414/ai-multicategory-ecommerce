"""Brief: View Customers (id, name, email, mobile_number, address, registered_date, status) and
Activate / Deactivate Customer."""

from django.contrib import messages
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.models import Customer
from accounts.services import set_customer_status
from adminpanel.views.common import paginate, query_without_page, safe_next
from core.permissions import admin_required
from orders.services.queries import order_groups


@admin_required
def customer_list(request):
    q = request.GET.get("q", "").strip()
    status = request.GET.get("status", "")
    customers = Customer.objects.annotate(order_count=Count("orders__order_id", distinct=True)).order_by("-registered_date")
    if q:
        customers = customers.filter(Q(name__icontains=q) | Q(email__icontains=q) | Q(mobile_number__icontains=q))
    if status in Customer.Status.values:
        customers = customers.filter(status=status)
    return render(request, "adminpanel/customers/list.html", {
        "section": "customers", "page": paginate(request, customers), "q": q, "status": status,
        "qs": query_without_page(request),
    })


@admin_required
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    return render(request, "adminpanel/customers/detail.html", {
        "section": "customers", "customer": customer, "orders": order_groups(customer.orders.all()),
    })


@admin_required
@require_POST
def customer_set_status(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    status = request.POST.get("status")
    if status not in Customer.Status.values:
        messages.error(request, "Choose Active or Inactive.")
    else:
        set_customer_status(customer, status)
        verb = "activated" if status == Customer.Status.ACTIVE else "deactivated"
        messages.success(request, f"{customer.name}’s account was {verb}.")
    return redirect(safe_next(request, customer.get_admin_url()))
