"""Admin login and logout (brief: Login (username, password), Logout)."""

from django.contrib import messages
from django.contrib.auth import login, logout
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from accounts.forms import AdminLoginForm


def admin_login(request):
    """Staff-only sign-in. Wrong details or a customer account get the same generic error."""
    if request.user.is_authenticated and request.user.is_staff:
        return redirect("adminpanel:dashboard")
    form = AdminLoginForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.user, backend="django.contrib.auth.backends.ModelBackend")
        messages.success(request, f"Signed in as {form.user.username}.")
        target = request.POST.get("next", "")
        if target and url_has_allowed_host_and_scheme(target, allowed_hosts={request.get_host()}):
            return redirect(target)
        return redirect("adminpanel:dashboard")
    return render(request, "adminpanel/login.html", {"form": form, "next": request.GET.get("next", "")})


@require_POST
def admin_logout(request):
    logout(request)
    messages.success(request, "You have signed out of the admin panel.")
    return redirect("adminpanel:login")
