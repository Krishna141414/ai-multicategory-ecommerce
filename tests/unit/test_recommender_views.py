"""Recommendation pages: similar products, Recommended for you, the AI Explainer and its JSON."""

from decimal import Decimal

import pytest
from django.urls import reverse

from accounts.services import register_customer
from catalog.models import Category, Product

pytestmark = [pytest.mark.unit, pytest.mark.ai, pytest.mark.django_db]


@pytest.fixture
def products():
    electronics = Category.objects.create(category_name="Electronics")
    kitchen = Category.objects.create(category_name="Kitchen and Home Appliances")
    rows = [
        (electronics, "Arc Wireless Earbuds", "earbuds, bluetooth, wireless, noise cancelling"),
        (electronics, "Field Over-Ear Headphones", "headphones, bluetooth, wireless, noise cancelling"),
        (electronics, "Pocket Bluetooth Speaker", "speaker, bluetooth, wireless, portable"),
        (kitchen, "Electric Kettle", "kettle, stainless steel, tea, boil"),
        (kitchen, "Pressure Cooker", "pressure cooker, stainless steel, cooking"),
    ]
    return {name: Product.objects.create(category=cat, product_name=name, brand="Sonvale", price=Decimal("999.00"),
                                         description=f"{name} for everyday use.", keywords=kw, quantity=5)
            for cat, name, kw in rows}


@pytest.fixture
def signed_in(client):
    customer = register_customer(name="Asha Rao", email="asha@example.com", password="Velora#Test-2026",
                                 mobile_number="9876543210", address="14 Lakeview Apartments, Pune 411045")
    client.force_login(customer.user, backend="accounts.backends.EmailBackend")
    return client


def test_product_page_shows_similar_products(client, products):
    earbuds = products["Arc Wireless Earbuds"]
    response = client.get(earbuds.get_absolute_url())
    similar = response.context["similar"]
    assert similar and earbuds not in [r.product for r in similar]
    assert similar[0].product == products["Field Over-Ear Headphones"]
    body = response.content.decode()
    assert 'data-testid="similar-products"' in body and "Similar to Arc Wireless Earbuds" in body


def test_recommended_requires_login(client):
    assert reverse("accounts:login") in client.get(reverse("recommender:recommended"))["Location"]


def test_recommendations_follow_views_and_cart(signed_in, products):
    first = signed_in.get(reverse("recommender:recommended"))
    assert first.context["is_new"] and {r.score_label for r in first.context["recs"]} == {"Popularity"}
    signed_in.get(products["Electric Kettle"].get_absolute_url())  # logs a view
    recs = signed_in.get(reverse("recommender:recommended")).context["recs"]
    assert recs[0].product == products["Pressure Cooker"] and recs[0].reason == "Because you viewed Electric Kettle"
    assert products["Electric Kettle"] not in [r.product for r in recs]
    signed_in.post(reverse("orders:cart_add", args=[products["Arc Wireless Earbuds"].pk]), {"quantity": 1})  # logs a cart add
    recs = signed_in.get(reverse("recommender:recommended")).context["recs"]
    assert recs[0].reason == "Because you added Arc Wireless Earbuds"


def test_home_shows_popular_when_signed_out(client, products):
    response = client.get(reverse("core:home"))
    assert response.context["recs"] and not response.context["personal"]
    assert "Popular right now" in response.content.decode()


def test_explainer_page_is_public_and_follows_the_choice(client, products):
    kettle = products["Electric Kettle"]
    response = client.get(reverse("recommender:explainer"), {"product": kettle.pk})
    assert response.status_code == 200 and response.context["product"] == kettle
    body = response.content.decode()
    for n in range(1, 6):
        assert f'data-testid="explainer-step-{n}"' in body
    assert response.context["data"]["top"][0].product == products["Pressure Cooker"]
    # an unknown id falls back to a real product instead of failing
    assert client.get(reverse("recommender:explainer"), {"product": "99999"}).status_code == 200


def test_explainer_json(client, products):
    data = client.get(reverse("recommender:explainer_data", args=[products["Arc Wireless Earbuds"].pk])).json()
    assert data["raw"]["product_name"] == "Arc Wireless Earbuds" and data["terms"]
    scores = [s["score"] for s in data["scores"]]
    assert scores == sorted(scores, reverse=True)
    assert data["top"][0]["name"] == "Field Over-Ear Headphones" and data["top"][0]["category"] == "Electronics"
    assert client.get(reverse("recommender:explainer_data", args=[99999])).status_code == 404
