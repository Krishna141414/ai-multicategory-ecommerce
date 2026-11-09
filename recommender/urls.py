from django.urls import path

from recommender import views

app_name = "recommender"

urlpatterns = [
    path("recommendations/", views.recommended, name="recommended"),
    path("ai/explainer/", views.explainer, name="explainer"),
    path("ai/explainer/data/<int:product_id>/", views.explainer_data, name="explainer_data"),
]
