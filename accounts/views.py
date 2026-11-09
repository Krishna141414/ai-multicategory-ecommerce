"""Customer registration, login/logout and profile pages."""

from django.contrib import messages
from django.contrib.auth import login, logout
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from accounts import services
from accounts.forms import CustomerLoginForm, ProfileForm, RegistrationForm
from core.permissions import customer_required, get_customer

BACKEND = "accounts.backends.EmailBackend"


def _next_url(request, fallback: str = "core:home") -> str:
    """Where to go after login: a safe ?next= on this site, else the fallback."""
    target = request.POST.get("next") or request.GET.get("next")
    if target and url_has_allowed_host_and_scheme(target, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        return target
    return fallback


def register(request):
    """Brief: Registration. New customers are Active and signed in straight away."""
    if get_customer(request):
        return redirect("core:home")
    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        data = form.cleaned_data
        customer = services.register_customer(name=data["name"], email=data["email"], password=data["password1"],
                                              mobile_number=data["mobile_number"], address=data["address"])
        login(request, customer.user, backend=BACKEND)
        messages.success(request, f"Welcome to Chowk, {customer.first_name}. Your account is ready.")
        return redirect(_next_url(request))
    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    """Brief: Login (email, password)."""
    if get_customer(request):
        return redirect(_next_url(request))
    form = CustomerLoginForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.user, backend=BACKEND)
        messages.success(request, f"Signed in. Good to see you, {form.user.customer.first_name}.")
        return redirect(_next_url(request))
    return render(request, "accounts/login.html", {"form": form, "next": request.GET.get("next", "")})


@require_POST
def logout_view(request):
    """Brief: Logout. POST only, so a link or prefetch can never sign someone out."""
    logout(request)
    messages.success(request, "You have signed out.")
    return redirect("core:home")


@customer_required
def profile(request):
    """Brief: View Profile."""
    return render(request, "accounts/profile.html", {"customer": request.customer})


@customer_required
def profile_edit(request):
    """Brief: Update Profile."""
    form = ProfileForm(request.POST or None, instance=request.customer)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Your profile has been updated.")
        return redirect("accounts:profile")
    return render(request, "accounts/profile_edit.html", {"form": form, "customer": request.customer})
