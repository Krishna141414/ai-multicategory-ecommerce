"""Controlled test data. Every browser test builds exactly what it needs with these helpers, so it can run
alone and in any order (the test database is flushed between tests)."""

from decimal import Decimal

from django.contrib.auth.models import User

from accounts.services import register_customer
from catalog.models import Category, Product
from orders.models import Order, OrderStatus, Payment

PASSWORD = "Velora#Test-2026"
ADMIN_USERNAME = "storeadmin"

# Two aisles with keyword-rich products, so the recommender has clear neighbours.
SHOP = {
    "Electronics": [
        ("Arc Wireless Earbuds", "Sonvale", "2499.00", "3999.00", 10, "earbuds, bluetooth, wireless, noise cancelling",
         "Bluetooth earbuds with active noise cancelling and a pocket charging case."),
        ("Field Over-Ear Headphones", "Sonvale", "6990.00", None, 8, "headphones, bluetooth, wireless, noise cancelling",
         "Wireless over-ear headphones with noise cancelling for long trips."),
        ("Pocket Bluetooth Speaker", "Lumora", "1799.00", None, 12, "speaker, bluetooth, wireless, portable",
         "A small wireless speaker, splash proof, twelve hours of music."),
        ("4K Smart TV", "Lumora", "27990.00", None, 0, "television, 4k, smart tv, streaming",
         "A 43-inch 4K television with streaming apps built in."),
    ],
    "Kitchen and Home Appliances": [
        ("Electric Kettle", "Tadka Home", "1099.00", "1399.00", 20, "kettle, stainless steel, tea, boil",
         "A stainless steel kettle that boils water for tea in minutes."),
        ("Pressure Cooker", "Tadka Home", "1899.00", None, 15, "pressure cooker, stainless steel, cooking",
         "A stainless steel pressure cooker for dal and rice."),
        ("Hand Blender", "Brewmate", "1299.00", None, 9, "blender, kitchen, soups, smoothies",
         "A hand blender for soups and smoothies."),
    ],
}


def make_shop() -> dict[str, Product]:
    """Create the two aisles above. Returns products by name (the TV is out of stock on purpose)."""
    products = {}
    for category_name, rows in SHOP.items():
        category = Category.objects.create(category_name=category_name, description=f"{category_name} for every day.")
        for name, brand, price, mrp, qty, keywords, description in rows:
            products[name] = Product.objects.create(
                category=category, product_name=name, brand=brand, price=Decimal(price),
                mrp=Decimal(mrp) if mrp else None, quantity=qty, keywords=keywords, description=description)
    return products


def make_admin() -> User:
    return User.objects.create_user(username=ADMIN_USERNAME, password=PASSWORD, email="admin@example.com",
                                    is_staff=True, is_superuser=True)


def make_customer(name="Asha Rao", email="asha@example.com", mobile="9876543210",
                  address="14 Lakeview Apartments, Pune 411045"):
    return register_customer(name=name, email=email, password=PASSWORD, mobile_number=mobile, address=address)


def make_order(customer, items: list[tuple[Product, int]], status=OrderStatus.CONFIRMED, order_id="ORD-20261101-TEST",
               paid=True) -> str:
    """An order straight in the database (one row per item, shared order_id), optionally with a success payment."""
    total = Decimal("0")
    for product, qty in items:
        row = Order.objects.create(order_id=order_id, customer=customer, product=product, product_name=product.product_name,
                                   quantity=qty, price=product.price, order_status=status)
        total += row.amount
    if paid:
        Payment.objects.create(order_id=order_id, customer=customer, total_amount=total, payment_method="UPI",
                               payment_status=Payment.Status.SUCCESS, reference=f"PAY-{order_id[-6:]}")
    return order_id
