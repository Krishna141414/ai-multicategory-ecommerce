"""Page objects: one small class per screen the tests drive, so each test reads like the steps a person takes.
Locators use roles, labels, visible text and data-testid only (brief rule 8)."""

import re

from playwright.sync_api import Page, expect


class BasePage:
    path = "/"

    def __init__(self, page: Page, site: str):
        self.page = page
        self.site = site

    def open(self, path: str | None = None):
        self.page.goto(self.site + (path or self.path))
        return self

    def toast(self, text: str | re.Pattern):
        return self.page.get_by_test_id("toast").filter(has_text=text)


class CustomerLoginPage(BasePage):
    path = "/account/login/"

    def sign_in(self, email: str, password: str):
        self.page.get_by_label("Email").fill(email)
        self.page.get_by_label("Password", exact=True).fill(password)
        self.page.get_by_test_id("login-submit").click()


class RegisterPage(BasePage):
    path = "/account/register/"

    def register(self, name: str, email: str, mobile: str, address: str, password: str):
        self.page.get_by_label("Full name").fill(name)
        self.page.get_by_label("Email").fill(email)
        self.page.get_by_label("Mobile number").fill(mobile)
        self.page.get_by_label("Delivery address").fill(address)
        self.page.get_by_label("Password", exact=True).fill(password)
        self.page.get_by_label("Confirm password").fill(password)
        self.page.get_by_test_id("register-submit").click()


class AdminLoginPage(BasePage):
    path = "/manage/login/"

    def sign_in(self, username: str, password: str):
        self.page.get_by_label("Username").fill(username)
        self.page.get_by_label("Password", exact=True).fill(password)
        self.page.get_by_test_id("admin-login-submit").click()


class ProductPage(BasePage):
    def open_product(self, product):
        return self.open(product.get_absolute_url())

    def add_to_cart(self, quantity: int = 1):
        self.page.get_by_label("Quantity", exact=True).fill(str(quantity))
        self.page.get_by_test_id("add-to-cart").click()
        expect(self.toast("to your cart")).to_be_visible()


class CartPage(BasePage):
    path = "/cart/"

    def line(self, product_name: str):
        return self.page.get_by_test_id("cart-item").filter(has_text=product_name)

    def set_quantity(self, product_name: str, quantity: int):
        box = self.page.get_by_label(f"Quantity of {product_name}", exact=True)
        box.fill(str(quantity))
        box.press("Tab")  # the change event sends the update

    def remove(self, product_name: str):
        self.line(product_name).get_by_test_id("remove-item").click()
        self.page.get_by_test_id("confirm-ok").click()  # "Remove … from your cart?"

    def total(self):
        return self.page.get_by_test_id("cart-total").first

    def check_out(self):
        self.page.get_by_test_id("checkout-button").click()


class CheckoutPage(BasePage):
    path = "/checkout/"

    def place_order(self):
        self.page.get_by_test_id("place-order").click()
        expect(self.page.get_by_test_id("payment-form")).to_be_visible()


class PaymentPage(BasePage):
    METHODS = {"Card": "method-card", "UPI": "method-upi", "Net Banking": "method-net-banking"}

    def pay(self, method: str = "UPI", succeed: bool = True):
        self.page.get_by_test_id(self.METHODS[method]).check()
        self.page.get_by_test_id("outcome-success" if succeed else "outcome-failure").check()
        self.page.get_by_test_id("pay-button").click()

    def order_id(self) -> str:
        return self.page.get_by_test_id("payment-order-id").inner_text().strip()
