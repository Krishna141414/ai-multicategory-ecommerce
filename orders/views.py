"""Cart, checkout, dummy payment, confirmation and order history (customer side)."""

import uuid

from django.contrib import messages
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from catalog.models import Product
from core.permissions import customer_required
from orders.forms import PaymentForm
from orders.models import Order, Payment
from orders.services import cart as cart_service
from orders.services.cart import CartError
from orders.services.checkout import CheckoutError, is_paid, order_rows, order_total, submit_cart
from orders.services.payment import pay
from orders.services.queries import order_groups

CHECKOUT_KEY = "checkout_key"


def wants_json(request) -> bool:
    return "application/json" in request.headers.get("Accept", "")


def _quantity(request, default: int = 1) -> int | None:
    try:
        return int(request.POST.get("quantity", default))
    except (TypeError, ValueError):
        return None


@customer_required
def cart(request):
    """Brief: View Cart."""
    return render(request, "orders/cart.html", {"cart": cart_service.get_cart(request.customer)})


@customer_required
@require_POST
def cart_add(request, product_id: int):
    """Brief: Add to Cart (login required; blocks zero stock and quantities above stock)."""
    product = get_object_or_404(Product, pk=product_id)
    quantity = _quantity(request)
    try:
        if quantity is None:
            raise CartError("Choose a quantity.")
        cart_service.add_to_cart(request.customer, product, quantity)
    except CartError as exc:
        if wants_json(request):
            return JsonResponse({"ok": False, "message": str(exc)}, status=400)
        messages.error(request, str(exc))
        return redirect(product.get_absolute_url())
    count = cart_service.cart_count(request.customer)
    message = f"Added {product.product_name} to your cart."
    if wants_json(request):
        return JsonResponse({"ok": True, "message": message, "count": count, "cart_url": reverse("orders:cart")})
    messages.success(request, message)
    return redirect("orders:cart")


@customer_required
@require_POST
def cart_update(request, item_id: int):
    """Brief: Update Cart Quantity."""
    quantity = _quantity(request)
    try:
        if quantity is None:
            raise CartError("Choose a quantity.")
        cart_service.update_quantity(request.customer, item_id, quantity)
    except CartError as exc:
        if wants_json(request):
            return JsonResponse({"ok": False, "message": str(exc)}, status=400)
        messages.error(request, str(exc))
        return redirect("orders:cart")
    if wants_json(request):
        return JsonResponse(_cart_json(request.customer, item_id))
    messages.success(request, "Quantity updated.")
    return redirect("orders:cart")


@customer_required
@require_POST
def cart_remove(request, item_id: int):
    """Brief: Remove from Cart."""
    try:
        name = cart_service.remove_item(request.customer, item_id)
    except CartError as exc:
        messages.error(request, str(exc))
    else:
        messages.success(request, f"Removed {name} from your cart.")
    return redirect("orders:cart")


def _cart_json(customer, item_id: int) -> dict:
    from core.templatetags.shop_tags import inr

    summary = cart_service.get_cart(customer)
    line = next((l for l in summary.lines if l.item.pk == item_id), None)
    return {"ok": True, "count": summary.count, "total": inr(summary.total), "problems": summary.has_problems,
            "line_total": inr(line.line_total) if line else None, "line_problem": line.problem if line else ""}


@customer_required
def checkout(request):
    """Review the order, then Submit Cart (creates Pending order rows and reserves stock)."""
    customer = request.customer
    summary = cart_service.get_cart(customer)
    if request.method == "POST":
        key = request.POST.get(CHECKOUT_KEY, "")
        if key != request.session.get(CHECKOUT_KEY):
            messages.error(request, "This checkout page is out of date. Please review your order again.")
            return redirect("orders:checkout")
        try:
            order_id = submit_cart(customer, key)
        except CheckoutError as exc:
            messages.error(request, str(exc))
            return redirect("orders:cart")
        return redirect("orders:payment", order_id=order_id)
    if summary.is_empty:
        messages.info(request, "Your cart is empty.")
        return redirect("orders:cart")
    if summary.has_problems:
        messages.error(request, "Some items in your cart need attention before you can check out.")
        return redirect("orders:cart")
    key = uuid.uuid4().hex
    request.session[CHECKOUT_KEY] = key  # one key per review page: a double submit reuses the same order
    return render(request, "orders/checkout.html", {"cart": summary, "customer": customer, "checkout_key": key})


def _own_rows(request, order_id: str):
    rows = list(order_rows(order_id).filter(customer=request.customer))
    if not rows:
        raise Http404("Order not found")
    return rows


@customer_required
def payment(request, order_id: str):
    """Brief: Dummy Payment. The customer picks a method and whether the payment succeeds."""
    rows = _own_rows(request, order_id)
    if is_paid(order_id):
        return redirect("orders:confirmation", order_id=order_id)
    if rows[0].order_status == "Cancelled":
        messages.error(request, "This order was cancelled, so it can't be paid. Please check out again.")
        return redirect("orders:cart")
    form = PaymentForm(request.POST or None)
    failed = None
    if request.method == "POST" and form.is_valid():
        try:
            result = pay(request.customer, order_id, form.cleaned_data["payment_method"], form.cleaned_data["outcome"])
        except CheckoutError as exc:
            messages.error(request, str(exc))
            return redirect("orders:cart")
        if result.succeeded:
            return redirect("orders:confirmation", order_id=order_id)
        failed = result.payment
    attempts = Payment.objects.filter(order_id=order_id, payment_status=Payment.Status.FAILED).count()
    return render(request, "orders/payment.html", {
        "order_id": order_id, "rows": rows, "total": order_total(order_id), "form": form,
        "failed": failed, "attempts": attempts,
    }, status=200)


@customer_required
def confirmation(request, order_id: str):
    """Brief: View Order Confirmation."""
    rows = _own_rows(request, order_id)
    if not is_paid(order_id):
        return redirect("orders:payment", order_id=order_id)
    paid = Payment.objects.get(order_id=order_id, payment_status=Payment.Status.SUCCESS)
    return render(request, "orders/confirmation.html", {
        "order_id": order_id, "rows": rows, "total": order_total(order_id), "payment": paid, "customer": request.customer,
    })


@customer_required
def history(request):
    """Brief: View Order History (grouped by order_id, with status)."""
    groups = order_groups(Order.objects.filter(customer=request.customer), with_rows=True)
    return render(request, "orders/history.html", {"orders": groups})


TRACK = ["Pending", "Confirmed", "Shipped", "Delivered"]


def status_track(status: str) -> list[tuple[str, str]]:
    """Steps for the order progress bar: done / current / upcoming (all upcoming if cancelled)."""
    if status not in TRACK:
        return [(name, "") for name in TRACK]
    current = TRACK.index(status)
    return [(name, "is-done" if i < current else "is-current" if i == current else "") for i, name in enumerate(TRACK)]


@customer_required
def detail(request, order_id: str):
    """Brief: View Order Details."""
    rows = _own_rows(request, order_id)
    status = rows[0].order_status
    return render(request, "orders/detail.html", {
        "order_id": order_id, "rows": rows, "status": status, "total": order_total(order_id), "track": status_track(status),
        "payments": Payment.objects.filter(order_id=order_id).order_by("-payment_date"), "paid": is_paid(order_id),
        "customer": request.customer,
    })
