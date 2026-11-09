from django.urls import path

from .views import auth, dashboard

app_name = "adminpanel"

urlpatterns = [
    path("login/", auth.admin_login, name="login"),
    path("logout/", auth.admin_logout, name="logout"),
    path("", dashboard.dashboard, name="dashboard"),
]
