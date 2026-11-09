"""Brief: Add / View / Update / Delete Product, plus the sponsored toggle."""

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from adminpanel.forms import ProductForm
from adminpanel.views.common import paginate, query_without_page, safe_next
from catalog.models import Category, Product, Status
from catalog.services import admin_product_list, delete_product
from core.permissions import admin_required


@admin_required
def product_list(request):
    products = admin_product_list(request.GET)
    return render(request, "adminpanel/products/list.html", {
        "section": "products", "page": paginate(request, products, 25), "qs": query_without_page(request),
        "categories": Category.objects.order_by("category_name"), "filters": request.GET,
        "total": products.count(),
    })


@admin_required
def product_create(request):
    form = ProductForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        product = form.save()
        messages.success(request, f"Product “{product.product_name}” added.")
        return redirect("adminpanel:product_detail", pk=product.pk)
    return render(request, "adminpanel/products/form.html", {"section": "products", "form": form})


@admin_required
def product_detail(request, pk):
    product = get_object_or_404(Product.objects.select_related("category"), pk=pk)
    return render(request, "adminpanel/products/detail.html", {
        "section": "products", "product": product, "order_count": product.orders.values("order_id").distinct().count(),
    })


@admin_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"Product “{product.product_name}” updated.")
        return redirect("adminpanel:product_detail", pk=product.pk)
    return render(request, "adminpanel/products/form.html", {"section": "products", "form": form, "product": product})


@admin_required
@require_POST
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    name = product.product_name
    result = delete_product(product)
    if result == "deactivated":
        messages.warning(request, f"“{name}” has orders, so it was hidden from the store (status Inactive) instead of deleted. Order history is kept.")
    else:
        messages.success(request, f"Product “{name}” deleted.")
    return redirect("adminpanel:products")


@admin_required
@require_POST
def product_toggle_sponsored(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.is_sponsored = not product.is_sponsored
    if product.is_sponsored and product.status != Status.ACTIVE:
        messages.error(request, "Only active products can be sponsored.")
        return redirect(safe_next(request, "adminpanel:products"))
    product.save(update_fields=["is_sponsored", "updated_at"])
    state = "added to" if product.is_sponsored else "removed from"
    messages.success(request, f"“{product.product_name}” {state} the sponsored deals strip.")
    return redirect(safe_next(request, "adminpanel:products"))
