from django.urls import path

from .views import auth, categories, customers, dashboard, orders, products, queries, reviews

app_name = "adminpanel"

urlpatterns = [
    path("login/", auth.admin_login, name="login"),
    path("logout/", auth.admin_logout, name="logout"),
    path("", dashboard.dashboard, name="dashboard"),
    # Categories
    path("categories/", categories.category_list, name="categories"),
    path("categories/new/", categories.category_create, name="category_create"),
    path("categories/<int:pk>/edit/", categories.category_edit, name="category_edit"),
    path("categories/<int:pk>/delete/", categories.category_delete, name="category_delete"),
    # Products
    path("products/", products.product_list, name="products"),
    path("products/new/", products.product_create, name="product_create"),
    path("products/<int:pk>/", products.product_detail, name="product_detail"),
    path("products/<int:pk>/edit/", products.product_edit, name="product_edit"),
    path("products/<int:pk>/delete/", products.product_delete, name="product_delete"),
    path("products/<int:pk>/sponsored/", products.product_toggle_sponsored, name="product_toggle_sponsored"),
    # Customers
    path("customers/", customers.customer_list, name="customers"),
    path("customers/<int:pk>/", customers.customer_detail, name="customer_detail"),
    path("customers/<int:pk>/status/", customers.customer_set_status, name="customer_set_status"),
    # Orders
    path("orders/", orders.order_list, name="orders"),
    path("orders/<str:order_id>/", orders.order_detail, name="order_detail"),
    path("orders/<str:order_id>/status/", orders.order_update_status, name="order_update_status"),
    # Ratings & reviews
    path("reviews/", reviews.review_list, name="reviews"),
    # Queries
    path("queries/", queries.query_inbox, name="queries"),
    path("queries/new/", queries.query_new, name="query_new"),
    path("queries/<str:conversation_id>/", queries.query_thread, name="query_thread"),
]
