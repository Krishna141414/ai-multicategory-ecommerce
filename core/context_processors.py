"""Values every template needs: store name, category menu (+ mega menu), cart count."""

from django.conf import settings
from django.utils.functional import SimpleLazyObject

from catalog.models import Category, Status
from catalog.services import mega_menu
from core.permissions import get_customer


def store_context(request) -> dict:
    customer = get_customer(request) if hasattr(request, "user") else None
    cart_count = 0
    if customer is not None:
        cart_count = sum(customer.cart_items.values_list("quantity", flat=True))
    return {
        "STORE_NAME": settings.STORE_NAME,
        "ASSET_VERSION": settings.ASSET_VERSION,
        "nav_categories": Category.objects.filter(status=Status.ACTIVE).only("category_name", "slug"),
        "mega_menu": SimpleLazyObject(mega_menu),  # only queried when a page renders the menu
        "current_customer": customer,
        "cart_count": cart_count,
    }
