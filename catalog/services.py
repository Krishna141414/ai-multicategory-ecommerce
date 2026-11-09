"""Catalogue rules used by the admin panel and the storefront."""

from django.db import transaction
from django.db.models import Avg, Count, Q, QuerySet

from catalog.models import Category, Product, Status


class CategoryInUse(Exception):
    """Raised when a category still has products and therefore can't be deleted."""


def delete_category(category: Category) -> None:
    """Delete an empty category. A category with products is kept (every product needs one).

    Raises CategoryInUse with a message the admin can act on.
    """
    count = category.products.count()
    if count:
        raise CategoryInUse(
            f"“{category.category_name}” still has {count} product{'s' if count != 1 else ''}. "
            "Move or delete them first, or set the category to Inactive to hide it."
        )
    category.delete()


@transaction.atomic
def delete_product(product: Product) -> str:
    """Delete a product, or hide it if customers have ordered it.

    Returns "deleted" (removed for good) or "deactivated" (status Inactive, kept for order history,
    brief rule 2: products with orders keep their historical order information).
    """
    if product.orders.exists():
        product.status = Status.INACTIVE
        product.is_sponsored = False
        product.save(update_fields=["status", "is_sponsored", "updated_at"])
        product.cart_items.all().delete()  # nobody can buy a hidden product
        return "deactivated"
    product.delete()
    return "deleted"


def with_ratings(queryset: QuerySet[Product]) -> QuerySet[Product]:
    """Annotate products with avg_rating and rating_count."""
    return queryset.annotate(avg_rating=Avg("ratings__rating"), rating_count=Count("ratings", distinct=True))


def admin_product_list(params: dict) -> QuerySet[Product]:
    """Admin product list filtered by search text, category, status, stock and sponsored flag."""
    qs = Product.objects.select_related("category").order_by("-added_date")
    text = (params.get("q") or "").strip()
    if text:
        qs = qs.filter(Q(product_name__icontains=text) | Q(brand__icontains=text) | Q(keywords__icontains=text))
    if params.get("category"):
        qs = qs.filter(category_id=params["category"])
    if params.get("status") in (Status.ACTIVE, Status.INACTIVE):
        qs = qs.filter(status=params["status"])
    stock = params.get("stock")
    if stock == "out":
        qs = qs.filter(quantity=0)
    elif stock == "low":
        qs = qs.filter(quantity__gt=0, quantity__lte=5)
    if params.get("sponsored") == "1":
        qs = qs.filter(is_sponsored=True)
    return qs
