"""Storefront catalogue: search by name / category / price (combinable), validation, detail page."""

from decimal import Decimal

import pytest
from django.urls import reverse

from accounts.services import register_customer
from catalog.models import Category, Product, Status
from catalog.services import search_products
from recommender.models import CustomerProductInteraction

pytestmark = [pytest.mark.unit, pytest.mark.django_db]


@pytest.fixture
def catalog():
    electronics = Category.objects.create(category_name="Electronics")
    kitchen = Category.objects.create(category_name="Kitchen and Home Appliances")
    make = lambda cat, name, brand, price, qty=10, kw="", status=Status.ACTIVE: Product.objects.create(
        category=cat, product_name=name, brand=brand, price=Decimal(price), quantity=qty, keywords=kw,
        description=f"{name} by {brand}.", status=status)
    return {
        "earbuds": make(electronics, "Arc 3 Wireless Earbuds", "Sonvale", "2499", kw="earbuds, bluetooth"),
        "speaker": make(electronics, "Pocket Bluetooth Speaker", "Sonvale", "1799", kw="speaker, bluetooth"),
        "tv": make(electronics, "43-inch 4K Smart TV", "Lumora", "27990", qty=0, kw="smart tv"),
        "kettle": make(kitchen, "Electric Kettle, 1.5 L", "Brewmate", "1099", kw="kettle"),
        "hidden": make(kitchen, "Old Toaster", "Brewmate", "999", status=Status.INACTIVE),
        "electronics": electronics, "kitchen": kitchen,
    }


def names(qs):
    return sorted(p.product_name for p in qs)


def test_search_by_name_icontains(catalog):
    assert names(search_products({"product_name": "earbuds"})) == ["Arc 3 Wireless Earbuds"]
    assert names(search_products({"product_name": "BLUETOOTH"})) == ["Arc 3 Wireless Earbuds", "Pocket Bluetooth Speaker"]


def test_search_by_category(catalog):
    assert names(search_products({"category": catalog["kitchen"]})) == ["Electric Kettle, 1.5 L"]


def test_search_by_price_range(catalog):
    result = search_products({"min_price": Decimal("1000"), "max_price": Decimal("2000")})
    assert names(result) == ["Electric Kettle, 1.5 L", "Pocket Bluetooth Speaker"]


def test_combined_filters(catalog):
    result = search_products({"product_name": "sonvale", "category": catalog["electronics"], "max_price": Decimal("2000")})
    assert names(result) == ["Pocket Bluetooth Speaker"]


def test_inactive_products_hidden(catalog):
    assert "Old Toaster" not in names(search_products({}))
    url = reverse("catalog:product_detail", args=[catalog["hidden"].slug])
    from django.test import Client
    assert Client().get(url).status_code == 404


def test_sort_by_price(catalog):
    prices = [p.price for p in search_products({"sort": "price_asc"})]
    assert prices == sorted(prices)


def test_invalid_price_range_shows_error(client, catalog):
    response = client.get(reverse("catalog:product_list"), {"min_price": "5000", "max_price": "100"})
    assert response.status_code == 200
    assert "The maximum price must be higher than the minimum price." in response.content.decode()
    response = client.get(reverse("catalog:product_list"), {"min_price": "abc", "max_price": "-5"})
    assert response.status_code == 200 and "Enter a minimum price" in response.content.decode()


def test_empty_result_state(client, catalog):
    response = client.get(reverse("catalog:product_list"), {"product_name": "zzz-nothing"})
    assert 'data-testid="empty-results"' in response.content.decode()


def test_category_page_and_grid(client, catalog):
    response = client.get(reverse("catalog:category", args=[catalog["electronics"].slug]))
    listed = [p.product_name for p in response.context["page"]]  # the grid only (the mega menu lists every aisle)
    assert "Arc 3 Wireless Earbuds" in listed and "Electric Kettle" not in listed
    grid = client.get(reverse("catalog:category_list")).content.decode()
    assert "Electronics" in grid and "Kitchen and Home Appliances" in grid


def test_product_detail_shows_fields_and_out_of_stock(client, catalog):
    body = client.get(reverse("catalog:product_detail", args=[catalog["tv"].slug])).content.decode()
    for text in ("43-inch 4K Smart TV", "Lumora", "Electronics", "₹27,990.00", "Out of stock", "0 available"):
        assert text in body
    assert 'data-testid="add-to-cart"' not in body


def test_product_view_is_logged_for_customers_once(client, catalog):
    customer = register_customer(name="Asha Rao", email="asha@example.com", password="Velora#Test-2026",
                                 mobile_number="9876543210", address="14 Lakeview Apartments, Pune 411045")
    url = reverse("catalog:product_detail", args=[catalog["earbuds"].slug])
    client.get(url)  # guest view: not logged
    assert CustomerProductInteraction.objects.count() == 0
    client.force_login(customer.user, backend="accounts.backends.EmailBackend")
    client.get(url)
    client.get(url)  # refresh within 10 minutes counts once
    views = CustomerProductInteraction.objects.filter(customer=customer, product=catalog["earbuds"], interaction_type="view")
    assert views.count() == 1
