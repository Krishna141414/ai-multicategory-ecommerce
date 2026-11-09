"""Admin dashboard (filled in during Phase 4.1)."""

from django.shortcuts import render

from core.permissions import admin_required


@admin_required
def dashboard(request):
    return render(request, "adminpanel/dashboard.html", {"section": "dashboard"})
