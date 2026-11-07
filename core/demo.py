"""Demo data used by `manage.py seed_demo` and `manage.py reset_demo`.

Every function is idempotent: running it twice leaves the same data.
Past orders are history only, so they do not change current stock.
"""

import os
from datetime import timedelta
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify

from accounts.models import Customer
from accounts.services import default_admin
from catalog.models import Category, Product
from catalog.seed_data import CATEGORIES, DEMO_CUSTOMERS, PRODUCTS
from messaging.models import Message, Role
from orders.models import CartItem, Order, OrderStatus, Payment
from recommender.models import CustomerProductInteraction
from reviews.models import Rating, Review

# (customer email, days ago, status, payment method or None, [(product slug, qty)], {slug: (stars, review text)})
DEMO_ORDERS = [
    ("asha.rao@example.com", 50, "Delivered", "Card",
     [("hearthline-smart-plug-pack-of-2", 1), ("voltrek-20000-mah-power-bank", 1), ("keystrand-silent-wireless-mouse", 1)],
     {"hearthline-smart-plug-pack-of-2": (4, "Set up in five minutes. I put the geyser on a schedule and stopped forgetting it on."),
      "voltrek-20000-mah-power-bank": (5, "Charged my phone four times on a Goa trip. A bit heavy, but that is the trade-off."),
      "keystrand-silent-wireless-mouse": (4, "")}),
    ("asha.rao@example.com", 20, "Delivered", "Card",
     [("sonvale-arc-3-wireless-earbuds", 1), ("chargelink-33-w-usb-c-fast-charger", 1)],
     {"sonvale-arc-3-wireless-earbuds": (5, "Noise cancelling is good enough for the traffic on my commute. Battery easily lasts the day."),
      "chargelink-33-w-usb-c-fast-charger": (4, "Small and charges fast. Gets slightly warm.")}),
    ("asha.rao@example.com", 3, "Shipped", "UPI",
     [("orvia-nova-5g-smartphone-8-gb-128-gb", 1), ("shieldguard-rugged-case-for-nova", 1),
      ("shieldguard-tempered-glass-screen-protector-for-nova", 1)], {}),
    ("rahul.menon@example.com", 60, "Delivered", "Net Banking",
     [("nestwell-queen-size-cotton-bedsheet-set", 2), ("nestwell-memory-foam-pillow", 2), ("gameshala-wooden-chess-set", 1)],
     {"nestwell-queen-size-cotton-bedsheet-set": (4, "Nice crisp cotton. The colour has held after a dozen washes."),
      "nestwell-memory-foam-pillow": (3, "Comfortable, but a little too high for me."),
      "gameshala-wooden-chess-set": (5, "")}),
    ("rahul.menon@example.com", 35, "Delivered", "UPI",
     [("tadka-home-mixer-grinder-750-w-3-jars", 1), ("steelwell-stainless-steel-pressure-cooker-5-l", 1)],
     {"tadka-home-mixer-grinder-750-w-3-jars": (5, "Grinds coconut chutney smooth in under a minute. Loud, like every mixer."),
      "steelwell-stainless-steel-pressure-cooker-5-l": (4, "Solid build and works on our induction stove.")}),
    ("rahul.menon@example.com", 1, "Confirmed", "UPI",
     [("brewmate-electric-kettle-15-l", 2)], {}),
    ("priya.sharma@example.com", 40, "Delivered", "Card",
     [("neem-ash-neem-and-tea-tree-face-wash", 2), ("mitti-naturals-onion-hair-oil", 1), ("inkwell-co-gel-pens-pack-of-10", 1)],
     {"neem-ash-neem-and-tea-tree-face-wash": (4, "Does not dry out my skin. Works well in the Jaipur heat."),
      "mitti-naturals-onion-hair-oil": (3, "The smell takes getting used to. Less hair fall after a month.")}),
    ("priya.sharma@example.com", 15, "Delivered", "UPI",
     [("indigo-loom-womens-block-print-straight-kurta", 2), ("dewlab-10-vitamin-c-face-serum", 1)],
     {"indigo-loom-womens-block-print-straight-kurta": (5, "Lovely print and the cotton is soft. Ordered my usual size and it fits."),
      "dewlab-10-vitamin-c-face-serum": (4, "")}),
    ("priya.sharma@example.com", 10, "Cancelled", None,
     [("thread-thali-womens-minimalist-analog-watch", 1)], {}),
]

DEMO_CART = {
    "asha.rao@example.com": [("sonvale-field-700-over-ear-headphones", 1)],
    "priya.sharma@example.com": [("dewlab-spf-50-sunscreen-gel", 1)],
}

DEMO_VIEWS = {
    "asha.rao@example.com": ["sonvale-field-700-over-ear-headphones", "sonvale-pocket-bluetooth-speaker",
                             "orvia-fit-smartwatch-with-calling", "ferrow-trail-action-camera"],
    "rahul.menon@example.com": ["tadka-home-digital-air-fryer-42-l", "brewmate-drip-coffee-maker",
                                "chakki-pro-table-top-wet-grinder-2-l"],
    "priya.sharma@example.com": ["kaarigar-co-handloom-cotton-saree", "dewlab-spf-50-sunscreen-gel",
                                 "kesari-botanicals-kumkumadi-face-oil"],
}

# (customer email, subject, customer message, admin reply or None, days ago)
DEMO_CONVERSATIONS = [
    ("asha.rao@example.com", "When will my phone arrive?",
     "Hi, my order with the Orvia Nova shipped on Monday. Is there an expected delivery date for Pune?",
     "Hi Asha, it is with the courier and should reach Baner by Thursday evening. We will message you if that changes.", 2),
    ("rahul.menon@example.com", "Mixer grinder jar sizes",
     "Could you tell me the capacity of each of the three jars that come with the Tadka Home mixer grinder?", None, 1),
]


def product_image_name(brand: str, product_name: str) -> str:
    """Relative media path where a seed product's photo is stored."""
    return f"products/{slugify(f'{brand} {product_name}')}.jpg"


def seed_catalog() -> tuple[int, int]:
    """Create or update the 10 categories and their products. Returns (categories, products)."""
    for name, description in CATEGORIES:
        Category.objects.update_or_create(category_name=name, defaults={"description": description})

    count = 0
    for category_name, rows in PRODUCTS.items():
        category = Category.objects.get(category_name=category_name)
        for name, brand, price, mrp, qty, keywords, description, sponsored, _query in rows:
            image = product_image_name(brand, name)
            has_image = (Path(settings.MEDIA_ROOT) / image).exists()
            Product.objects.update_or_create(
                slug=slugify(f"{brand} {name}"),
                defaults={
                    "category": category,
                    "product_name": name,
                    "brand": brand,
                    "price": Decimal(price),
                    "mrp": Decimal(mrp) if mrp else None,
                    "quantity": qty,
                    "keywords": keywords,
                    "description": description,
                    "is_sponsored": sponsored,
                    "image": image if has_image else "",
                },
            )
            count += 1
    return len(CATEGORIES), count


def seed_customers() -> list[Customer]:
    """The four demo shoppers. Their password comes from DEMO_CUSTOMER_PASSWORD in .env."""
    password = os.getenv("DEMO_CUSTOMER_PASSWORD", "")
    if not password:
        raise ValueError("Set DEMO_CUSTOMER_PASSWORD in .env first.")
    customers = []
    for name, email, mobile, address in DEMO_CUSTOMERS:
        user, created = User.objects.get_or_create(username=email, defaults={"email": email, "first_name": name.split()[0]})
        if created:
            user.set_password(password)
            user.save()
        customer, _ = Customer.objects.update_or_create(
            user=user, defaults={"name": name, "email": email, "mobile_number": mobile, "address": address})
        customers.append(customer)
    return customers


def _order_id(when, n: int) -> str:
    return f"ORD-{when:%Y%m%d}-DM{n:02d}"


def seed_orders() -> int:
    """Past orders with payments, purchase interactions, ratings and reviews. Returns the number of orders."""
    now = timezone.now()
    for n, (email, days, status, method, items, feedback) in enumerate(DEMO_ORDERS, start=1):
        customer = Customer.objects.get(email=email)
        when = now - timedelta(days=days)
        if Order.objects.filter(order_id__endswith=f"-DM{n:02d}", customer=customer).exists():
            continue
        order_id = _order_id(when, n)
        total = Decimal("0")
        for slug, qty in items:
            product = Product.objects.get(slug=slug)
            row = Order.objects.create(order_id=order_id, customer=customer, product=product,
                                       product_name=product.product_name, quantity=qty, price=product.price,
                                       order_date=when, order_status=status)
            total += row.amount
            if status != OrderStatus.CANCELLED:
                CustomerProductInteraction.objects.create(customer=customer, product=product,
                                                          interaction_type="purchase", interaction_date=when)
        if method:
            Payment.objects.create(order_id=order_id, customer=customer, total_amount=total, payment_method=method,
                                   payment_status=Payment.Status.SUCCESS, payment_date=when,
                                   reference=f"PAY-DEMO-{n:04d}")
        for slug, (stars, text) in feedback.items():
            product = Product.objects.get(slug=slug)
            posted = when + timedelta(days=min(days, 6))
            Rating.objects.update_or_create(product=product, customer=customer,
                                            defaults={"rating": stars, "posted_date": posted})
            if text:
                Review.objects.update_or_create(product=product, customer=customer,
                                                defaults={"review": text, "posted_date": posted})
    return Order.objects.values("order_id").distinct().count()


def seed_carts_and_views() -> None:
    """A couple of items left in carts, and recent product views, so recommendations have signal."""
    now = timezone.now()
    for email, items in DEMO_CART.items():
        customer = Customer.objects.get(email=email)
        for slug, qty in items:
            product = Product.objects.get(slug=slug)
            _, created = CartItem.objects.get_or_create(customer=customer, product=product, defaults={"quantity": qty})
            if created:
                CustomerProductInteraction.objects.create(customer=customer, product=product, interaction_type="cart",
                                                          interaction_date=now - timedelta(hours=5))
    for email, slugs in DEMO_VIEWS.items():
        customer = Customer.objects.get(email=email)
        if customer.interactions.filter(interaction_type="view").exists():
            continue
        for i, slug in enumerate(slugs):
            CustomerProductInteraction.objects.create(customer=customer, product=Product.objects.get(slug=slug),
                                                      interaction_type="view",
                                                      interaction_date=now - timedelta(days=i + 1))


def seed_conversations() -> int:
    """Two customer queries: one answered by the admin, one still unread."""
    admin = default_admin()
    if admin is None:
        raise ValueError("Run create_default_admin first.")
    now = timezone.now()
    for n, (email, subject, text, reply, days) in enumerate(DEMO_CONVERSATIONS, start=1):
        conversation_id = f"CNV-DEMO{n:04d}"
        if Message.objects.filter(conversation_id=conversation_id).exists():
            continue
        customer = Customer.objects.get(email=email)
        first = Message.objects.create(
            conversation_id=conversation_id, sender=customer.user, sender_type=Role.CUSTOMER, receiver=admin,
            receiver_type=Role.ADMIN, subject=subject, message=text, posted_date=now - timedelta(days=days),
            status=Message.Status.READ if reply else Message.Status.UNREAD)
        if reply:
            Message.objects.create(
                conversation_id=conversation_id, sender=admin, sender_type=Role.ADMIN, receiver=customer.user,
                receiver_type=Role.CUSTOMER, parent_message=first, subject=f"Re: {subject}", message=reply,
                posted_date=now - timedelta(days=days) + timedelta(hours=3))
    return Message.objects.values("conversation_id").distinct().count()
