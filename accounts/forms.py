"""Customer forms. All validation runs on the server (brief rule 9)."""

import re

from django import forms
from django.contrib.auth import authenticate, password_validation
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from accounts.models import Customer
from accounts.services import login_error_for

MOBILE_PATTERN = re.compile(r"^[6-9]\d{9}$")


def clean_mobile(value: str) -> str:
    """Accept '98765 43210', '+91 9876543210' or '09876543210'; store 10 digits."""
    digits = re.sub(r"\D", "", value or "")
    if len(digits) == 12 and digits.startswith("91"):
        digits = digits[2:]
    elif len(digits) == 11 and digits.startswith("0"):
        digits = digits[1:]
    if not MOBILE_PATTERN.match(digits):
        raise ValidationError("Enter a 10-digit Indian mobile number starting with 6, 7, 8 or 9.")
    return digits


def email_taken(email: str, exclude_customer: Customer | None = None) -> bool:
    customers = Customer.objects.filter(email__iexact=email)
    users = User.objects.filter(username__iexact=email) | User.objects.filter(email__iexact=email)
    if exclude_customer is not None:
        customers = customers.exclude(pk=exclude_customer.pk)
        users = users.exclude(pk=exclude_customer.user_id)
    return customers.exists() or users.exists()


class RegistrationForm(forms.Form):
    """Brief: Registration (name, email, mobile_number, password, address)."""

    name = forms.CharField(label="Full name", max_length=120,
                           widget=forms.TextInput(attrs={"autocomplete": "name"}))
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={"autocomplete": "email", "spellcheck": "false"}))
    mobile_number = forms.CharField(label="Mobile number", max_length=16,
                                    widget=forms.TextInput(attrs={"autocomplete": "tel", "inputmode": "tel"}),
                                    help_text="10 digits, for delivery updates.")
    address = forms.CharField(label="Delivery address", max_length=500,
                              widget=forms.Textarea(attrs={"rows": 3, "autocomplete": "street-address"}))
    password1 = forms.CharField(label="Password", strip=False,
                                widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
                                help_text="At least 8 characters, not just numbers.")
    password2 = forms.CharField(label="Confirm password", strip=False,
                                widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}))

    def clean_name(self):
        name = " ".join(self.cleaned_data["name"].split())
        if len(name) < 2:
            raise ValidationError("Enter your full name.")
        return name

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if email_taken(email):
            raise ValidationError("An account with this email already exists. Sign in instead.")
        return email

    def clean_mobile_number(self):
        return clean_mobile(self.cleaned_data["mobile_number"])

    def clean_address(self):
        address = self.cleaned_data["address"].strip()
        if len(address) < 10:
            raise ValidationError("Enter your full delivery address.")
        return address

    def clean(self):
        cleaned = super().clean()
        p1, p2 = cleaned.get("password1"), cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "The two passwords don't match.")
        elif p1:
            probe = User(username=cleaned.get("email", ""), email=cleaned.get("email", ""), first_name=cleaned.get("name", ""))
            try:
                password_validation.validate_password(p1, probe)
            except ValidationError as exc:
                self.add_error("password1", exc)
        return cleaned


class CustomerLoginForm(forms.Form):
    """Brief: Login (email, password)."""

    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={"autocomplete": "email", "spellcheck": "false", "autofocus": True}))
    password = forms.CharField(label="Password", strip=False,
                               widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}))

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned = super().clean()
        email, password = cleaned.get("email"), cleaned.get("password")
        if email and password:
            self.user = authenticate(self.request, email=email, password=password)
            if self.user is None:
                raise ValidationError(login_error_for(email, password), code="invalid_login")
        return cleaned


class AdminLoginForm(forms.Form):
    """Brief: Admin Login (username, password). Only staff accounts may sign in here."""

    username = forms.CharField(label="Username", max_length=150,
                               widget=forms.TextInput(attrs={"autocomplete": "username", "spellcheck": "false", "autocapitalize": "none", "autofocus": True}))
    password = forms.CharField(label="Password", strip=False,
                               widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}))

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned = super().clean()
        username, password = cleaned.get("username"), cleaned.get("password")
        if username and password:
            user = authenticate(self.request, username=username, password=password)
            if user is None or not user.is_staff:
                raise ValidationError("Username or password is incorrect.", code="invalid_login")
            self.user = user
        return cleaned


class ProfileForm(forms.ModelForm):
    """Brief: Update Profile. Email stays unique (case-insensitive)."""

    class Meta:
        model = Customer
        fields = ["name", "email", "mobile_number", "address"]
        labels = {"name": "Full name", "mobile_number": "Mobile number", "address": "Delivery address"}
        widgets = {
            "name": forms.TextInput(attrs={"autocomplete": "name"}),
            "email": forms.EmailInput(attrs={"autocomplete": "email", "spellcheck": "false"}),
            "mobile_number": forms.TextInput(attrs={"autocomplete": "tel", "inputmode": "tel"}),
            "address": forms.Textarea(attrs={"rows": 3, "autocomplete": "street-address"}),
        }

    def clean_name(self):
        name = " ".join(self.cleaned_data["name"].split())
        if len(name) < 2:
            raise ValidationError("Enter your full name.")
        return name

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if email_taken(email, exclude_customer=self.instance):
            raise ValidationError("Another account already uses this email.")
        return email

    def clean_mobile_number(self):
        return clean_mobile(self.cleaned_data["mobile_number"])

    def clean_address(self):
        address = self.cleaned_data["address"].strip()
        if len(address) < 10:
            raise ValidationError("Enter your full delivery address.")
        return address

    def save(self, commit=True):
        customer = super().save(commit=False)
        user = customer.user
        user.email = user.username = customer.email
        user.first_name = customer.name.split()[0]
        if commit:
            customer.save()
            user.save(update_fields=["email", "username", "first_name"])
        return customer
