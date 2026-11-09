"""Storefront home page and error pages."""

from django.shortcuts import render

from core.permissions import get_customer
from recommender.engine import get_engine, popular

HOME_RECS = 6


def home(request):
    """Home: "Recommended for you" (personalised for signed-in customers, popular picks otherwise)."""
    customer = get_customer(request)
    recs = get_engine().personalized(customer, top_n=HOME_RECS) if customer else popular(HOME_RECS)
    return render(request, "core/home.html", {"recs": recs, "personal": customer is not None})
