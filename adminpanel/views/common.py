"""Helpers shared by the admin views."""

from django.core.paginator import Paginator


def paginate(request, items, per_page: int = 20):
    """Return the requested page of `items` (?page=N), clamped to a valid page."""
    return Paginator(items, per_page).get_page(request.GET.get("page"))


def query_without_page(request) -> str:
    """The current query string minus ?page=, for building pagination links."""
    params = request.GET.copy()
    params.pop("page", None)
    return params.urlencode()


def safe_next(request, default: str) -> str:
    """A ?next= / POST next URL on this site, or `default` (never redirect off-site)."""
    from django.utils.http import url_has_allowed_host_and_scheme

    target = request.POST.get("next") or request.GET.get("next")
    if target and url_has_allowed_host_and_scheme(target, allowed_hosts={request.get_host()}):
        return target
    return default
