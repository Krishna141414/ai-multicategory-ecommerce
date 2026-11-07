"""URL map. Customer pages at the root, admin panel under /manage/."""

from django.conf import settings
from django.urls import include, path, re_path
from django.views.static import serve

urlpatterns = [
    path("", include("core.urls")),
    path("account/", include("accounts.urls")),
    path("", include("catalog.urls")),
    path("", include("orders.urls")),
    path("", include("reviews.urls")),
    path("queries/", include("messaging.urls")),
    path("", include("recommender.urls")),
    path("manage/", include("adminpanel.urls")),
]

# Product images are served by Django in every mode: this store runs locally only
# (brief rule 10) and the test live server runs with DEBUG=False.
urlpatterns += [
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
]
