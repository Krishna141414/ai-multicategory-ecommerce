"""Data the recommender learns from (brief: AI Product Recommendation tables).

ProductFeature: id, product_id, category, product_name, brand, description, keywords, price
CustomerProductInteraction: id, customer_id, product_id, interaction_type, interaction_date
"""

from django.db import models
from django.utils import timezone

from accounts.models import Customer
from catalog.models import Product


class ProductFeature(models.Model):
    """A flat copy of the text the engine vectorises. Kept in sync by recommender.signals."""

    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name="feature")
    category = models.CharField(max_length=100)
    product_name = models.CharField(max_length=160)
    brand = models.CharField(max_length=80)
    description = models.TextField()
    keywords = models.CharField(max_length=300, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Features of {self.product_name}"


class CustomerProductInteraction(models.Model):
    class Type(models.TextChoices):
        VIEW = "view", "Viewed"
        CART = "cart", "Added to cart"
        PURCHASE = "purchase", "Purchased"

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="interactions")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="interactions")
    interaction_type = models.CharField(max_length=10, choices=Type.choices)
    interaction_date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-interaction_date"]
        indexes = [models.Index(fields=["customer", "-interaction_date"])]

    def __str__(self) -> str:
        return f"{self.customer_id} {self.interaction_type} {self.product_id}"
