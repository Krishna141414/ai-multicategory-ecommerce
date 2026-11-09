"""Storefront catalogue: categories, product listing/search, product details."""

from django.core.paginator import Paginator
from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404, render

from catalog import services
from catalog.forms import ProductSearchForm
from catalog.models import Category, Product, Status
from core.permissions import get_customer
from recommender.interactions import VIEW, log_interaction

PER_PAGE = 12


def _query_without(request, *names: str) -> str:
    params = request.GET.copy()
    for name in names:
        params.pop(name, None)
    return params.urlencode()


def category_list(request):
    """Brief: View Product Categories."""
    categories = list(services.storefront_categories())
    for category in categories:
        category.cover = services.category_cover(category)
    return render(request, "catalog/categories.html", {"categories": categories})


def product_list(request, category_slug: str | None = None):
    """Brief: View Products + Search Product (product_name, category, min_price, max_price)."""
    category = None
    data = request.GET.copy()
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug, status=Status.ACTIVE)
        data["category"] = category.slug
    form = ProductSearchForm(data)
    if form.is_valid():
        products = services.search_products(form.cleaned_data)
    else:
        # invalid input (e.g. min > max): show the error and every product rather than a broken page
        products = services.search_products({})
    page = Paginator(products, PER_PAGE).get_page(request.GET.get("page"))
    chips = [(name, label, _query_without(request, name, "page")) for name, label in form.active_filters()
             if not (category and name == "category")]
    return render(request, "catalog/product_list.html", {
        "form": form, "page": page, "category": category, "chips": chips,
        "total": page.paginator.count, "qs": _query_without(request, "page"),
        "searching": bool(request.GET.get("product_name")),
    })


def product_detail(request, slug: str):
    """Brief: View Product Details (product_name, category, brand, price, description, image,
    available_quantity, rating). Logs a `view` interaction for the recommender."""
    product = get_object_or_404(Product.objects.active().select_related("category"), slug=slug)
    stats = product.ratings.aggregate(avg=Avg("rating"), count=Count("id"))
    customer = get_customer(request)
    log_interaction(customer, product, VIEW)
    return render(request, "catalog/product_detail.html", {
        "product": product, "avg_rating": stats["avg"], "rating_count": stats["count"],
        "breakdown": services.rating_breakdown(product), "reviews": services.product_reviews(product),
        "max_qty": min(product.quantity, 10),
    })
