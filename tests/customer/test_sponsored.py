"""Sponsored deals strip with hover quick view, and the admin's sponsored toggle (CLAUDE.md must-have extra 1).
Not catalogue cases (the catalogue mirrors the brief's list); they run and are recorded with every suite run."""

import pytest
from playwright.sync_api import expect

from catalog.models import Product
from orders.models import CartItem
from tests.factories import make_admin, make_customer, make_shop

pytestmark = [pytest.mark.customer, pytest.mark.django_db(transaction=True)]


@pytest.fixture
def sponsored_shop():
    """Every product sponsored: seven deals, more than fit on screen, so the strip drifts."""
    shop = make_shop()
    Product.objects.update(is_sponsored=True)
    return shop


def test_few_deals_stay_still_without_controls(page, site):
    shop = make_shop()
    Product.objects.filter(pk__in=[shop["Arc Wireless Earbuds"].pk, shop["Electric Kettle"].pk]).update(is_sponsored=True)
    page.goto(f"{site}/")
    expect(page.get_by_test_id("sponsored-strip").get_by_test_id("sponsored-item")).to_have_count(2)
    for control in ("sponsored-prev", "sponsored-toggle", "sponsored-next"):
        expect(page.get_by_test_id(control)).to_be_hidden()  # nothing moves, so nothing to pause or scroll


def test_hovering_a_sponsored_deal_opens_quick_view_and_adds_to_cart(page, site, sponsored_shop, as_customer):
    customer = make_customer()
    as_customer(customer)
    page.goto(f"{site}/")
    strip = page.get_by_test_id("sponsored-strip")
    expect(strip.get_by_test_id("sponsored-item")).to_have_count(len(sponsored_shop))  # loop copies carry no test ids
    toggle = page.get_by_test_id("sponsored-toggle")
    toggle.click()  # pause the drift so the cards hold still
    expect(toggle).to_have_attribute("aria-pressed", "true")
    strip.get_by_test_id("sponsored-item").filter(has_text="Electric Kettle").hover()
    panel = page.get_by_test_id("quick-view-panel")
    expect(panel).to_be_visible()
    expect(panel.get_by_test_id("quick-view-name")).to_have_text("Electric Kettle")
    expect(panel.get_by_test_id("quick-view-price")).to_contain_text("₹1,099.00")
    expect(panel.get_by_test_id("quick-view-stock")).to_contain_text("In stock")
    panel.get_by_test_id("quick-view-add").click()
    expect(page.get_by_test_id("toast").filter(has_text="Added Electric Kettle")).to_be_visible()
    assert CartItem.objects.get(customer=customer).product == sponsored_shop["Electric Kettle"]
    page.keyboard.press("Escape")
    expect(panel).to_be_hidden()


@pytest.mark.admin
def test_admin_sponsored_toggle_puts_a_product_in_the_strip(page, site, as_admin):
    shop = make_shop()
    as_admin(make_admin())
    page.goto(f"{site}/manage/products/")
    switch = page.get_by_test_id("product-row").filter(has_text="Pressure Cooker").get_by_test_id("toggle-sponsored")
    expect(switch).to_have_attribute("aria-checked", "false")
    switch.click()
    expect(page.get_by_test_id("product-row").filter(has_text="Pressure Cooker").get_by_test_id("toggle-sponsored")).to_have_attribute("aria-checked", "true")
    assert Product.objects.get(pk=shop["Pressure Cooker"].pk).is_sponsored
    page.goto(f"{site}/")
    expect(page.get_by_test_id("sponsored-strip").get_by_test_id("sponsored-item").filter(has_text="Pressure Cooker")).to_be_visible()
