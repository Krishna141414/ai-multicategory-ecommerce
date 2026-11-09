"""Authentication and role rules (brief rules 1 and 9), tested with Django's test client."""

import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from accounts.models import Customer
from accounts.services import DEACTIVATED_MESSAGE, INVALID_LOGIN_MESSAGE, register_customer, set_customer_status

pytestmark = [pytest.mark.unit, pytest.mark.django_db]

PASSWORD = "Velora#Test-2026"
REGISTRATION = {
    "name": "Meera Iyer", "email": "Meera.Iyer@Example.com", "mobile_number": "+91 98450 12345",
    "address": "22 Temple Street, Malleshwaram, Bengaluru 560003", "password1": PASSWORD, "password2": PASSWORD,
}


@pytest.fixture
def customer():
    return register_customer(name="Asha Rao", email="asha@example.com", password=PASSWORD,
                             mobile_number="9876543210", address="14 Lakeview Apartments, Pune 411045")


@pytest.fixture
def admin_user():
    return User.objects.create_user(username="storeadmin", password=PASSWORD, is_staff=True)


def test_register_creates_active_customer(client):
    response = client.post(reverse("accounts:register"), REGISTRATION)
    assert response.status_code == 302
    customer = Customer.objects.get()
    assert customer.email == "meera.iyer@example.com"  # stored lower-case
    assert customer.mobile_number == "9845012345"  # normalised to 10 digits
    assert customer.status == Customer.Status.ACTIVE
    assert client.session.get("_auth_user_id") == str(customer.user_id)  # signed in after registering


def test_password_is_hashed(client):
    client.post(reverse("accounts:register"), REGISTRATION)
    user = Customer.objects.get().user
    assert user.password != PASSWORD and user.password.startswith(("pbkdf2_", "argon2", "scrypt", "md5$"))
    assert user.check_password(PASSWORD)


def test_duplicate_email_case_insensitive(client, customer):
    data = {**REGISTRATION, "email": "ASHA@example.com"}
    response = client.post(reverse("accounts:register"), data)
    assert response.status_code == 200
    assert "already exists" in response.content.decode()
    assert Customer.objects.count() == 1


def test_registration_rejects_bad_mobile_and_mismatched_passwords(client):
    data = {**REGISTRATION, "mobile_number": "12345", "password2": "Different#123"}
    response = client.post(reverse("accounts:register"), data)
    body = response.content.decode()
    assert response.status_code == 200 and Customer.objects.count() == 0
    assert "10-digit Indian mobile number" in body
    assert "The two passwords don&#x27;t match." in body


def test_customer_login_with_email(client, customer):
    response = client.post(reverse("accounts:login"), {"email": "ASHA@example.com", "password": PASSWORD})
    assert response.status_code == 302
    assert client.session.get("_auth_user_id") == str(customer.user_id)


def test_invalid_login_shows_generic_error(client, customer):
    response = client.post(reverse("accounts:login"), {"email": "asha@example.com", "password": "wrong-password"})
    assert INVALID_LOGIN_MESSAGE in response.content.decode()
    response = client.post(reverse("accounts:login"), {"email": "nobody@example.com", "password": PASSWORD})
    assert INVALID_LOGIN_MESSAGE in response.content.decode()


def test_inactive_customer_cannot_login(client, customer):
    set_customer_status(customer, Customer.Status.INACTIVE)
    response = client.post(reverse("accounts:login"), {"email": "asha@example.com", "password": PASSWORD})
    assert DEACTIVATED_MESSAGE in response.content.decode()
    assert "_auth_user_id" not in client.session
    # a wrong password on a deactivated account does not reveal its status
    response = client.post(reverse("accounts:login"), {"email": "asha@example.com", "password": "wrong"})
    assert INVALID_LOGIN_MESSAGE in response.content.decode()


def test_deactivated_session_is_logged_out(client, customer):
    client.force_login(customer.user, backend="accounts.backends.EmailBackend")
    assert client.get(reverse("accounts:profile")).status_code == 200
    set_customer_status(customer, Customer.Status.INACTIVE)
    response = client.get(reverse("accounts:profile"))
    assert response.status_code == 302 and reverse("accounts:login") in response["Location"]


def test_logout_requires_post(client, customer):
    client.force_login(customer.user, backend="accounts.backends.EmailBackend")
    assert client.get(reverse("accounts:logout")).status_code == 405
    client.post(reverse("accounts:logout"))
    assert "_auth_user_id" not in client.session


def test_profile_requires_login(client):
    response = client.get(reverse("accounts:profile"))
    assert response.status_code == 302 and reverse("accounts:login") in response["Location"]


def test_profile_update_keeps_email_unique(client, customer):
    register_customer(name="Ravi K", email="ravi@example.com", password=PASSWORD, mobile_number="9123456780",
                      address="5 MG Road, Kochi 682016")
    client.force_login(customer.user, backend="accounts.backends.EmailBackend")
    data = {"name": "Asha R", "email": "RAVI@example.com", "mobile_number": "9876543210", "address": customer.address}
    response = client.post(reverse("accounts:profile_edit"), data)
    assert response.status_code == 200 and "Another account already uses this email" in response.content.decode()
    data["email"] = "asha.new@example.com"
    response = client.post(reverse("accounts:profile_edit"), data)
    assert response.status_code == 302
    customer.refresh_from_db()
    assert customer.email == "asha.new@example.com" and customer.user.username == "asha.new@example.com"


def test_admin_login_with_username(client, admin_user):
    response = client.post(reverse("adminpanel:login"), {"username": "storeadmin", "password": PASSWORD})
    assert response.status_code == 302 and response["Location"] == reverse("adminpanel:dashboard")


def test_invalid_admin_login_and_customer_account_refused(client, admin_user, customer):
    response = client.post(reverse("adminpanel:login"), {"username": "storeadmin", "password": "nope"})
    assert "Username or password is incorrect." in response.content.decode()
    response = client.post(reverse("adminpanel:login"), {"username": "asha@example.com", "password": PASSWORD})
    assert "Username or password is incorrect." in response.content.decode()
    assert "_auth_user_id" not in client.session


def test_customer_cannot_open_admin(client, customer):
    client.force_login(customer.user, backend="accounts.backends.EmailBackend")
    assert client.get(reverse("adminpanel:dashboard")).status_code == 403


def test_guest_is_sent_to_admin_login(client):
    response = client.get(reverse("adminpanel:dashboard"))
    assert response.status_code == 302 and reverse("adminpanel:login") in response["Location"]


def test_admin_cannot_use_customer_pages(client, admin_user):
    client.force_login(admin_user)
    assert client.get(reverse("accounts:profile")).status_code == 403


def test_forms_carry_csrf_tokens(client):
    for name in ("accounts:login", "accounts:register", "adminpanel:login"):
        assert "csrfmiddlewaretoken" in client.get(reverse(name)).content.decode()
