"""Add Rating and Add Review (customer side). Both post from the product page and return to it."""

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

from catalog.models import Product
from core.permissions import customer_required
from reviews import services
from reviews.forms import RatingForm, ReviewForm


def _back(product: Product):
    return redirect(product.get_absolute_url() + "#your-feedback")


@customer_required
@require_POST
def rate(request, product_id: int):
    """Brief: Add Rating (1–5, buyers only, one per product; saving again updates it)."""
    product = get_object_or_404(Product.objects.active(), pk=product_id)
    form = RatingForm(request.POST)
    if not form.is_valid():
        messages.error(request, form.errors["rating"][0])
        return _back(product)
    try:
        _, created = services.save_rating(request.customer, product, form.cleaned_data["rating"])
    except services.ReviewError as exc:
        messages.error(request, str(exc))
    else:
        messages.success(request, "Thanks, your rating is saved." if created else "Your rating is updated.")
    return _back(product)


@customer_required
@require_POST
def review(request, product_id: int):
    """Brief: Add Review (buyers only, one per product; saving again updates it)."""
    product = get_object_or_404(Product.objects.active(), pk=product_id)
    form = ReviewForm(request.POST)
    if not form.is_valid():
        messages.error(request, form.errors["review"][0])
        return _back(product)
    try:
        _, created = services.save_review(request.customer, product, form.cleaned_data["review"])
    except services.ReviewError as exc:
        messages.error(request, str(exc))
    else:
        messages.success(request, "Thanks, your review is posted." if created else "Your review is updated.")
    return _back(product)
