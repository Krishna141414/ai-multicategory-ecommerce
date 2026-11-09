from django.urls import path

from reviews import views

app_name = "reviews"

urlpatterns = [
    path("product/<int:product_id>/rate/", views.rate, name="rate"),
    path("product/<int:product_id>/review/", views.review, name="review"),
]
