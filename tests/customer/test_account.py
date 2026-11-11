"""Customer account: registration, login, profile and logout (TC-CUS-01 to 05 and 27)."""

import re

import pytest
from playwright.sync_api import expect

from accounts.models import Customer
from tests.factories import PASSWORD, make_customer
from tests.pages import CustomerLoginPage, RegisterPage

pytestmark = [pytest.mark.customer, pytest.mark.django_db(transaction=True)]


@pytest.mark.tc("TC-CUS-01")
def test_customer_registration(page, site):
    RegisterPage(page, site).open().register("Meera Iyer", "meera@example.com", "9812345678",
                                             "22 Temple Street, Madurai 625001", PASSWORD)
    expect(page.get_by_test_id("toast").filter(has_text="Your account is ready")).to_be_visible()
    expect(page.get_by_test_id("account-menu")).to_contain_text("Meera")
    customer = Customer.objects.get(email="meera@example.com")
    assert customer.status == "Active" and customer.mobile_number == "9812345678"
    assert customer.user.check_password(PASSWORD)  # stored hashed, never as plain text
    assert customer.user.password != PASSWORD


@pytest.mark.tc("TC-CUS-02")
def test_customer_login(page, site):
    make_customer()
    CustomerLoginPage(page, site).open().sign_in("asha@example.com", PASSWORD)
    expect(page.get_by_test_id("toast").filter(has_text="Signed in")).to_be_visible()
    expect(page.get_by_test_id("account-menu")).to_contain_text("Asha")


@pytest.mark.negative
@pytest.mark.tc("TC-CUS-03")
def test_invalid_customer_login(page, site):
    make_customer()
    login = CustomerLoginPage(page, site).open()
    login.sign_in("asha@example.com", "wrong-password")
    expect(page.get_by_test_id("login-error")).to_be_visible()
    expect(page).to_have_url(re.compile(r"/account/login/"))
    expect(page.get_by_test_id("account-menu")).to_have_count(0)


@pytest.mark.tc("TC-CUS-04")
def test_view_profile(page, site, as_customer):
    as_customer(make_customer())
    page.goto(f"{site}/account/")
    expect(page.get_by_test_id("profile-name")).to_have_text("Asha Rao")
    expect(page.get_by_test_id("profile-email")).to_have_text("asha@example.com")
    expect(page.get_by_test_id("profile-mobile")).to_have_text("9876543210")
    expect(page.get_by_test_id("profile-address")).to_contain_text("Lakeview Apartments")
    expect(page.get_by_test_id("profile-status")).to_contain_text("Active")
    expect(page.get_by_test_id("profile-registered")).not_to_be_empty()


@pytest.mark.tc("TC-CUS-05")
def test_update_profile(page, site, as_customer):
    customer = make_customer()
    as_customer(customer)
    page.goto(f"{site}/account/edit/")
    page.get_by_label("Mobile number").fill("9900112233")
    page.get_by_label("Delivery address").fill("7 Park Lane, Bengaluru 560001")
    page.get_by_test_id("profile-save").click()
    expect(page.get_by_test_id("toast").filter(has_text="profile has been updated")).to_be_visible()
    expect(page.get_by_test_id("profile-mobile")).to_have_text("9900112233")
    customer.refresh_from_db()
    assert customer.mobile_number == "9900112233" and "Bengaluru" in customer.address


@pytest.mark.tc("TC-CUS-27")
def test_customer_logout(page, site, as_customer):
    as_customer(make_customer())
    page.goto(f"{site}/account/")
    page.get_by_test_id("account-menu").click()
    page.get_by_test_id("logout-button").click()
    expect(page.get_by_test_id("toast").filter(has_text="signed out")).to_be_visible()
    page.goto(f"{site}/cart/")
    expect(page).to_have_url(re.compile(r"/account/login/"))
