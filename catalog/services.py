"""Catalogue rules used by the admin panel and the storefront."""

from django.db import transaction
from django.db.models import Avg, Case, Count, IntegerField, Q, QuerySet, Value, When

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


# --- Storefront ------------------------------------------------------------------

SORTS = {
    "price_asc": ["price", "product_name"],
    "price_desc": ["-price", "product_name"],
    "newest": ["-added_date"],
    "rating": ["-avg_rating", "-rating_count", "product_name"],
}


def search_products(cleaned: dict) -> QuerySet[Product]:
    """Brief: Search Product by product_name, category, min_price, max_price (all combinable).

    Only active products in active categories are shown. Text matches the product name,
    brand or keywords. Results carry avg_rating and rating_count.
    """
    qs = with_ratings(Product.objects.active().select_related("category"))
    text = (cleaned.get("product_name") or "").strip()
    if text:
        for word in text.split():
            qs = qs.filter(Q(product_name__icontains=word) | Q(brand__icontains=word) | Q(keywords__icontains=word))
    if cleaned.get("category"):
        qs = qs.filter(category=cleaned["category"])
    if cleaned.get("min_price") is not None:
        qs = qs.filter(price__gte=cleaned["min_price"])
    if cleaned.get("max_price") is not None:
        qs = qs.filter(price__lte=cleaned["max_price"])
    if cleaned.get("in_stock"):
        qs = qs.filter(quantity__gt=0)
    sort = cleaned.get("sort") or "relevance"
    if sort in SORTS:
        return qs.order_by(*SORTS[sort])
    # "Featured": in-stock first, then sponsored, then best rated, then newest
    return qs.order_by(in_stock_first(), "-is_sponsored", "-avg_rating", "-added_date")


def in_stock_first():
    """Order key that puts out-of-stock products last."""
    return Case(When(quantity__gt=0, then=Value(0)), default=Value(1), output_field=IntegerField()).asc()


def storefront_categories() -> QuerySet[Category]:
    """Active categories with the number of products a customer can see."""
    return (Category.objects.filter(status=Status.ACTIVE)
            .annotate(product_count=Count("products", filter=Q(products__status=Status.ACTIVE)))
            .order_by("category_name"))


def category_cover(category: Category) -> Product | None:
    """A representative product photo for a category tile (sponsored or best stocked first)."""
    return (category.products.filter(status=Status.ACTIVE).exclude(image="")
            .order_by("-is_sponsored", "-quantity").first())


def product_reviews(product: Product) -> list[dict]:
    """Reviews for the product page, each with that customer's star rating when there is one."""
    from reviews.models import Rating, Review

    ratings = {r.customer_id: r.rating for r in Rating.objects.filter(product=product)}
    return [{"review": rv, "rating": ratings.get(rv.customer_id)}
            for rv in Review.objects.filter(product=product).select_related("customer").order_by("-posted_date")]


def rating_breakdown(product: Product) -> dict[int, int]:
    """How many 5, 4, 3, 2 and 1 star ratings the product has."""
    from reviews.models import Rating

    counts = {n: 0 for n in range(5, 0, -1)}
    for row in Rating.objects.filter(product=product).values("rating").annotate(n=Count("id")):
        counts[row["rating"]] = row["n"]
    return counts
