from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    path("cart/", views.cart, name="cart"),
    path("cart/add/<int:product_id>/", views.cart_add, name="cart_add"),
    path("cart/items/<int:item_id>/update/", views.cart_update, name="cart_update"),
    path("cart/items/<int:item_id>/remove/", views.cart_remove, name="cart_remove"),
    path("checkout/", views.checkout, name="checkout"),
    path("checkout/pay/<str:order_id>/", views.payment, name="payment"),
    path("orders/", views.history, name="history"),
    path("orders/<str:order_id>/", views.detail, name="detail"),
    path("orders/<str:order_id>/confirmed/", views.confirmation, name="confirmation"),
]
