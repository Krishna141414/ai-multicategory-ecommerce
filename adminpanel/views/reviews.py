"""Brief: View Product Ratings / Reviews."""

from django.db.models import Avg, Q
from django.shortcuts import render

from adminpanel.views.common import paginate, query_without_page
from core.permissions import admin_required
from reviews.models import Rating, Review


def _matches(q: str):
    return Q(product__product_name__icontains=q) | Q(customer__name__icontains=q)


@admin_required
def review_list(request):
    """One row per customer + product: the rating (1–5) and the review text, with the date."""
    q = request.GET.get("q", "").strip()
    stars = request.GET.get("rating", "")
    ratings = Rating.objects.select_related("product", "customer")
    reviews = Review.objects.select_related("product", "customer")
    if q:
        ratings, reviews = ratings.filter(_matches(q)), reviews.filter(_matches(q))
    if stars.isdigit():
        ratings = ratings.filter(rating=int(stars))
    review_by_key = {(r.product_id, r.customer_id): r for r in reviews}
    entries = [{"rating": r, "review": review_by_key.get((r.product_id, r.customer_id)), "product": r.product,
                "customer": r.customer, "date": r.posted_date} for r in ratings]
    if not stars:  # reviews that have no rating still need to show up
        rated = {(r.product_id, r.customer_id) for r in ratings}
        entries += [{"rating": None, "review": rv, "product": rv.product, "customer": rv.customer, "date": rv.posted_date}
                    for key, rv in review_by_key.items() if key not in rated]
    entries.sort(key=lambda e: e["date"], reverse=True)
    return render(request, "adminpanel/reviews/list.html", {
        "section": "reviews", "page": paginate(request, entries), "q": q, "stars": stars, "qs": query_without_page(request),
        "average": Rating.objects.aggregate(a=Avg("rating"))["a"], "rating_total": Rating.objects.count(),
        "review_total": Review.objects.count(),
    })
