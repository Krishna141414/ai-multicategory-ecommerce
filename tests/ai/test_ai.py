"""AI recommendations in the browser (TC-AI-01 to 08). Relevance is asserted, not just presence:
same category / shared keywords first, scores sorted, the product itself and unavailable products never shown."""

import pytest
from playwright.sync_api import expect

from recommender.interactions import PURCHASE, log_interaction
from recommender.models import ProductFeature
from tests.factories import make_customer, make_shop
from tests.pages import ProductPage

pytestmark = [pytest.mark.ai, pytest.mark.django_db(transaction=True)]


@pytest.fixture
def shop():
    return make_shop()


@pytest.fixture
def customer(as_customer):
    c = make_customer()
    as_customer(c)
    return c


def cards(page, where: str):
    return page.get_by_test_id(where).get_by_test_id("rec-card")


def scores(locator) -> list[float]:
    return [float(s) for s in locator.evaluate_all("els => els.map(e => e.dataset.score)")]


@pytest.mark.tc("TC-AI-01")
def test_product_feature_extraction(page, site, shop):
    earbuds = shop["Arc Wireless Earbuds"]
    feature = ProductFeature.objects.get(product=earbuds)  # kept in sync with the product
    assert (feature.category, feature.brand, feature.keywords) == ("Electronics", "Sonvale", earbuds.keywords)
    page.goto(f"{site}/ai/explainer/?product={earbuds.pk}")
    expect(page.get_by_test_id("explainer-raw")).to_contain_text("Arc Wireless Earbuds")
    expect(page.get_by_test_id("explainer-clean-text")).to_contain_text("noise cancelling")
    terms = page.get_by_test_id("explainer-terms").inner_text().lower()
    assert "earbuds" in terms or "noise cancelling" in terms  # its own keywords are among its strongest terms


@pytest.mark.tc("TC-AI-02")
def test_similar_product_recommendations(page, site, shop):
    earbuds = shop["Arc Wireless Earbuds"]
    ProductPage(page, site).open_product(earbuds)
    similar = cards(page, "similar-products")
    expect(similar.first).to_be_visible()
    ids = similar.evaluate_all("els => els.map(e => Number(e.dataset.productId))")
    assert earbuds.pk not in ids                                    # never itself
    assert shop["4K Smart TV"].pk not in ids                         # out of stock is never suggested
    assert scores(similar) == sorted(scores(similar), reverse=True)  # best first
    expect(similar.first).to_have_attribute("data-category", "Electronics")
    expect(similar.first.get_by_test_id("rec-name")).to_have_text("Field Over-Ear Headphones")  # shares 4 keywords


@pytest.mark.tc("TC-AI-03")
def test_customer_based_recommendations(page, site, shop, customer):
    log_interaction(customer, shop["Electric Kettle"], PURCHASE)  # what a confirmed payment logs
    page.goto(f"{site}/recommendations/")
    top = cards(page, "recommendations").first
    expect(top.get_by_test_id("rec-name")).to_have_text("Pressure Cooker")  # stainless steel, same aisle
    expect(top.get_by_test_id("rec-reason")).to_have_text("Because you bought Electric Kettle")


@pytest.mark.tc("TC-AI-04")
def test_recommended_product_display(page, site, shop, customer):
    log_interaction(customer, shop["Arc Wireless Earbuds"], PURCHASE)
    page.goto(f"{site}/recommendations/")
    recs = cards(page, "recommendations")
    expect(recs.first).to_be_visible()
    similarity = recs.filter(has=page.get_by_test_id("rec-score").filter(has_text="Similarity"))
    assert scores(similarity) == sorted(scores(similarity), reverse=True)
    ids = recs.evaluate_all("els => els.map(e => Number(e.dataset.productId))")
    assert shop["4K Smart TV"].pk not in ids and shop["Arc Wireless Earbuds"].pk not in ids


@pytest.mark.tc("TC-AI-05")
def test_recommended_product_details(page, site, shop):
    ProductPage(page, site).open_product(shop["Electric Kettle"])
    card = cards(page, "similar-products").first
    expect(card.get_by_test_id("rec-name")).not_to_be_empty()
    expect(card.get_by_test_id("rec-category")).to_have_text("Kitchen and Home Appliances")
    expect(card.get_by_role("img")).to_be_visible()
    expect(card.get_by_test_id("rec-price")).to_contain_text("₹")
    expect(card.get_by_test_id("rec-score")).to_contain_text("Similarity")
    assert 0 < float(card.get_attribute("data-score")) <= 1


@pytest.mark.tc("TC-AI-06")
def test_recommendation_after_product_view(page, site, shop, customer):
    ProductPage(page, site).open_product(shop["Electric Kettle"])  # the visit is logged as a view
    page.goto(f"{site}/recommendations/")
    top = cards(page, "recommendations").first
    expect(top.get_by_test_id("rec-reason")).to_have_text("Because you viewed Electric Kettle")
    expect(top).to_have_attribute("data-category", "Kitchen and Home Appliances")


@pytest.mark.tc("TC-AI-07")
def test_recommendation_after_adding_to_cart(page, site, shop, customer):
    ProductPage(page, site).open_product(shop["Pocket Bluetooth Speaker"]).add_to_cart(1)
    page.goto(f"{site}/recommendations/")
    recs = cards(page, "recommendations")
    expect(recs.first.get_by_test_id("rec-reason")).to_have_text("Because you added Pocket Bluetooth Speaker")
    expect(recs.first).to_have_attribute("data-category", "Electronics")
    ids = recs.evaluate_all("els => els.map(e => Number(e.dataset.productId))")
    assert shop["Pocket Bluetooth Speaker"].pk not in ids  # already in the cart


@pytest.mark.tc("TC-AI-08")
def test_recommendation_for_new_customer(page, site, shop, customer):
    page.goto(f"{site}/recommendations/")
    recs = cards(page, "recommendations")
    expect(recs.first).to_be_visible()
    labels = set(recs.get_by_test_id("rec-score").all_inner_texts())
    assert all("Popularity" in label for label in labels)
    expect(page.get_by_test_id("interest-list")).to_have_count(0)  # nothing personal to show yet
