from django.urls import path

from . import views

app_name = "catalog"

urlpatterns = [
    path("categories/", views.category_list, name="category_list"),
    path("category/<slug:category_slug>/", views.product_list, name="category"),
    path("products/", views.product_list, name="product_list"),
    path("product/<slug:slug>/", views.product_detail, name="product_detail"),
]
