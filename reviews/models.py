"""Ratings and reviews, kept in two tables as the brief lists them.

Add Rating: id, product_id, customer_id, rating, posted_date
Add Review: id, product_id, customer_id, review, posted_date
"""

from django.db import models
from django.db.models import Q
from django.utils import timezone

from accounts.models import Customer
from catalog.models import Product


class Rating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="ratings")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="ratings")
    rating = models.PositiveSmallIntegerField()
    posted_date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-posted_date"]
        constraints = [
            models.UniqueConstraint(fields=["product", "customer"], name="one_rating_per_customer_product"),
            models.CheckConstraint(condition=Q(rating__gte=1, rating__lte=5), name="rating_between_1_and_5"),
        ]

    def __str__(self) -> str:
        return f"{self.rating}/5 {self.product}"


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="reviews")
    review = models.TextField()
    posted_date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-posted_date"]
        constraints = [
            models.UniqueConstraint(fields=["product", "customer"], name="one_review_per_customer_product"),
        ]

    def __str__(self) -> str:
        return f"Review of {self.product} by {self.customer.name}"
