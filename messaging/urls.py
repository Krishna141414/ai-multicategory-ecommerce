from django.urls import path

from messaging import views

app_name = "messaging"

urlpatterns = [
    path("", views.query_list, name="list"),
    path("new/", views.query_new, name="new"),
    path("<str:conversation_id>/", views.query_thread, name="thread"),
]
