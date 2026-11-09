"""The recommender engine: features, TF-IDF terms, similarity, personalisation and the new-customer fallback."""

from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from accounts.services import register_customer
from catalog.models import Category, Product, Status
from orders.models import CartItem, Order, OrderStatus
from recommender.engine import clean_text, get_engine
from recommender.interactions import CART, PURCHASE, VIEW
from recommender.models import CustomerProductInteraction, ProductFeature

pytestmark = [pytest.mark.unit, pytest.mark.ai, pytest.mark.django_db]

CATALOGUE = {
    "Electronics": [
        ("Arc Wireless Earbuds", "Sonvale", "Bluetooth earbuds with active noise cancelling and a pocket charging case.",
         "earbuds, bluetooth, wireless, noise cancelling"),
        ("Field Over-Ear Headphones", "Sonvale", "Wireless over-ear headphones with noise cancelling for travel.",
         "headphones, bluetooth, wireless, noise cancelling"),
        ("Pocket Bluetooth Speaker", "Lumora", "Small wireless speaker, splash proof, twelve hours of music.",
         "speaker, bluetooth, wireless, portable"),
    ],
    "Kitchen and Home Appliances": [
        ("Electric Kettle", "Tadka Home", "Stainless steel kettle that boils water for tea in minutes.",
         "kettle, stainless steel, tea, boil"),
        ("Pressure Cooker", "Tadka Home", "Stainless steel pressure cooker for dal and rice.",
         "pressure cooker, stainless steel, cooking"),
    ],
    "Fashion and Clothing": [
        ("Cotton Kurta", "Thread and Thali", "Block-print cotton kurta for everyday wear.", "kurta, cotton, ethnic"),
        ("Handloom Cotton Saree", "Thread and Thali", "Soft handloom cotton saree with a woven border.", "saree, cotton, handloom, ethnic"),
    ],
}


@pytest.fixture
def products():
    made = {}
    for category_name, items in CATALOGUE.items():
        category = Category.objects.create(category_name=category_name)
        for name, brand, description, keywords in items:
            made[name] = Product.objects.create(category=category, product_name=name, brand=brand, price=Decimal("999.00"),
                                                description=description, keywords=keywords, quantity=10)
    return made


@pytest.fixture
def engine(products):
    return get_engine(force=True)


@pytest.fixture
def customer():
    return register_customer(name="Asha Rao", email="asha@example.com", password="Velora#Test-2026",
                             mobile_number="9876543210", address="14 Lakeview Apartments, Pune 411045")


def ids(recs):
    return [r.product.id for r in recs]


def test_clean_text():
    assert clean_text("<b>USB-C</b> Fast Charger, 33 W!") == "usb c fast charger w"


def test_feature_rows_follow_products(products):
    # brief table ProductFeature (product_id, category, product_name, brand, description, keywords, price)
    assert ProductFeature.objects.count() == len(products)
    kettle = products["Electric Kettle"]
    kettle.product_name = "Electric Kettle, 1.5 L"
    kettle.save()
    assert ProductFeature.objects.get(product=kettle).product_name == "Electric Kettle, 1.5 L"


def test_feature_matrix_shape(engine, products):
    assert engine.matrix.shape[0] == len(products)
    assert engine.similarity.shape == (len(products), len(products))


def test_top_terms_include_keywords(engine, products):
    terms = [t for t, _ in engine.top_terms(products["Arc Wireless Earbuds"].id)]
    assert "earbuds" in terms or "noise cancelling" in terms
    weights = [w for _, w in engine.top_terms(products["Arc Wireless Earbuds"].id)]
    assert weights == sorted(weights, reverse=True)


def test_similar_excludes_self(engine, products):
    earbuds = products["Arc Wireless Earbuds"]
    assert earbuds.id not in ids(engine.similar(earbuds.id))


def test_similar_same_category_first(engine, products):
    recs = engine.similar(products["Arc Wireless Earbuds"].id, top_n=2)
    assert {r.product.category.category_name for r in recs} == {"Electronics"}
    assert recs[0].product == products["Field Over-Ear Headphones"]  # shares bluetooth, wireless, noise cancelling
    kettle_recs = engine.similar(products["Electric Kettle"].id, top_n=1)
    assert kettle_recs[0].product == products["Pressure Cooker"]


def test_scores_sorted_desc_and_reason(engine, products):
    recs = engine.similar(products["Cotton Kurta"].id)
    scores = [r.score for r in recs]
    assert scores == sorted(scores, reverse=True) and all(0 < s <= 1 for s in scores)
    assert recs[0].score_label == "Similarity" and recs[0].reason.startswith("Similar to Cotton Kurta")


def test_similar_excludes_inactive_and_out_of_stock(engine, products):
    Product.objects.filter(pk=products["Field Over-Ear Headphones"].pk).update(status=Status.INACTIVE)
    Product.objects.filter(pk=products["Pocket Bluetooth Speaker"].pk).update(quantity=0)
    result = ids(engine.similar(products["Arc Wireless Earbuds"].id))
    assert products["Field Over-Ear Headphones"].id not in result
    assert products["Pocket Bluetooth Speaker"].id not in result


def test_personalized_uses_interests_and_excludes_them(engine, products, customer):
    earbuds, kettle = products["Arc Wireless Earbuds"], products["Electric Kettle"]
    CustomerProductInteraction.objects.create(customer=customer, product=earbuds, interaction_type=PURCHASE)
    CustomerProductInteraction.objects.create(customer=customer, product=kettle, interaction_type=VIEW,
                                              interaction_date=timezone.now() - timedelta(days=60))
    CartItem.objects.create(customer=customer, product=products["Pocket Bluetooth Speaker"], quantity=1)
    recs = engine.personalized(customer, top_n=3)
    assert earbuds.id not in ids(recs) and kettle.id not in ids(recs)
    assert products["Pocket Bluetooth Speaker"].id not in ids(recs)  # already in the cart
    assert recs[0].product == products["Field Over-Ear Headphones"]  # recent purchase outweighs an old view
    assert recs[0].reason == "Because you bought Arc Wireless Earbuds"


def test_interest_weights_purchase_over_cart_over_view(engine, products, customer):
    for name, kind in (("Cotton Kurta", VIEW), ("Electric Kettle", CART), ("Arc Wireless Earbuds", PURCHASE)):
        CustomerProductInteraction.objects.create(customer=customer, product=products[name], interaction_type=kind)
    weights = engine.interests(customer)
    assert weights[products["Arc Wireless Earbuds"].id]["weight"] > weights[products["Electric Kettle"].id]["weight"] \
        > weights[products["Cotton Kurta"].id]["weight"]


def test_new_customer_gets_popular(engine, products, customer):
    other = register_customer(name="Ravi Kumar", email="ravi@example.com", password="Velora#Test-2026",
                              mobile_number="9123456780", address="5 MG Road, Kochi 682016")
    saree = products["Handloom Cotton Saree"]
    Order.objects.create(order_id="ORD-T-1", customer=other, product=saree, product_name=saree.product_name,
                         quantity=3, price=saree.price, order_status=OrderStatus.DELIVERED)
    recs = engine.personalized(customer, top_n=4)
    assert recs[0].product == saree and recs[0].score_label == "Popularity" and recs[0].score == 1.0
    assert len(recs) == 4


def test_engine_rebuilds_when_products_change(engine, products):
    category = Category.objects.get(category_name="Electronics")
    Product.objects.create(category=category, product_name="Studio Wireless Earbuds", brand="Lumora", price=Decimal("1999.00"),
                           description="Wireless earbuds with noise cancelling.", keywords="earbuds, wireless, bluetooth", quantity=4)
    rebuilt = get_engine()
    assert rebuilt is not engine and rebuilt.matrix.shape[0] == len(products) + 1


def test_explain_payload(engine, products):
    data = engine.explain(products["Electric Kettle"].id)
    assert data["raw"]["product_name"] == "Electric Kettle"
    assert "stainless steel" in data["clean_text"] and data["terms"]
    assert [s["score"] for s in data["scores"]] == sorted((s["score"] for s in data["scores"]), reverse=True)
    assert data["top"][0].product == products["Pressure Cooker"]
