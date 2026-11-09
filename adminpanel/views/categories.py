"""Brief: Add / View / Update / Delete Category."""

from django.contrib import messages
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from adminpanel.forms import CategoryForm
from adminpanel.views.common import paginate, query_without_page
from catalog.models import Category
from catalog.services import CategoryInUse, delete_category
from core.permissions import admin_required


@admin_required
def category_list(request):
    q = request.GET.get("q", "").strip()
    categories = Category.objects.annotate(product_count=Count("products")).order_by("category_name")
    if q:
        categories = categories.filter(Q(category_name__icontains=q) | Q(description__icontains=q))
    return render(request, "adminpanel/categories/list.html", {
        "section": "categories", "page": paginate(request, categories), "q": q, "qs": query_without_page(request),
    })


@admin_required
def category_create(request):
    form = CategoryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        category = form.save()
        messages.success(request, f"Category “{category.category_name}” added.")
        return redirect("adminpanel:categories")
    return render(request, "adminpanel/categories/form.html", {"section": "categories", "form": form})


@admin_required
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    form = CategoryForm(request.POST or None, instance=category)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"Category “{category.category_name}” updated.")
        return redirect("adminpanel:categories")
    return render(request, "adminpanel/categories/form.html", {"section": "categories", "form": form, "category": category})


@admin_required
@require_POST
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    name = category.category_name
    try:
        delete_category(category)
    except CategoryInUse as exc:
        messages.error(request, str(exc))
    else:
        messages.success(request, f"Category “{name}” deleted.")
    return redirect("adminpanel:categories")
