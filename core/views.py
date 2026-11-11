"""Storefront home page."""

from django.shortcuts import render

from catalog import services as catalog
from catalog.models import Product
from core.permissions import get_customer
from recommender.engine import get_engine, popular

HOME_RECS = 6
SHELF = 8


def hero_offer() -> Product | None:
    """The deal in the hero: the sponsored, in-stock product with the biggest discount."""
    deals = [p for p in Product.objects.available().filter(is_sponsored=True).select_related("category") if p.discount_percent]
    return max(deals, key=lambda p: (p.discount_percent, p.price), default=None)


def home(request):
    """Home: hero offer, sponsored deals strip (quick view), the ten categories,
    "Recommended for you" (signed-in customers), best sellers and new arrivals."""
    customer = get_customer(request)
    categories = list(catalog.storefront_categories())
    for category in categories:
        category.cover = catalog.category_cover(category)
    best_sellers = [rec.product for rec in popular(SHELF)]
    return render(request, "core/home.html", {
        "hero": hero_offer(),
        "sponsored": catalog.with_ratings(Product.objects.active().filter(is_sponsored=True).select_related("category"))
                            .order_by("-quantity", "product_name"),
        "categories": categories,
        "recs": get_engine().personalized(customer, top_n=HOME_RECS) if customer else [],
        "best_sellers": best_sellers,
        "new_arrivals": catalog.with_ratings(Product.objects.available().select_related("category")).order_by("-added_date", "-id")[:SHELF],
    })
