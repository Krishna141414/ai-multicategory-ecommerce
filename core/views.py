"""Storefront home page and error pages."""

from django.shortcuts import render


def home(request):
    return render(request, "core/home.html")
