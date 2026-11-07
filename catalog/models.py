"""Catalogue: categories and products (brief: Add Category / Add Product fields)."""

from decimal import Decimal

from django.db import models
from django.db.models import F, Q
from django.templatetags.static import static
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


class Status(models.TextChoices):
    ACTIVE = "Active", "Active"
    INACTIVE = "Inactive", "Inactive"


def unique_slug(instance, value: str, max_length: int = 160) -> str:
    """Return a slug for `value` that no other row of the same model uses."""
    base = slugify(value)[: max_length - 6] or "item"
    slug, n = base, 2
    model = type(instance)
    while model.objects.filter(slug=slug).exclude(pk=instance.pk).exists():
        slug, n = f"{base}-{n}", n + 1
    return slug


class Category(models.Model):
    """Brief fields: id, category_name, description, status, created_date."""

    category_name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    created_date = models.DateTimeField(default=timezone.now)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    class Meta:
        ordering = ["category_name"]
        verbose_name_plural = "categories"

    def __str__(self) -> str:
        return self.category_name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, self.category_name, 120)
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        return reverse("catalog:category", args=[self.slug])

    @property
    def is_active(self) -> bool:
        return self.status == Status.ACTIVE


class ProductQuerySet(models.QuerySet):
    def active(self):
        """Products a customer may see: active product in an active category."""
        return self.filter(status=Status.ACTIVE, category__status=Status.ACTIVE)

    def available(self):
        """Active products that are also in stock (what the recommender may suggest)."""
        return self.active().filter(quantity__gt=0)


class Product(models.Model):
    """Brief fields: id, category_id, product_name, brand, price, description, image,
    quantity, keywords, added_date, status. Extras: mrp, is_sponsored, slug, updated_at."""

    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    product_name = models.CharField(max_length=160)
    brand = models.CharField(max_length=80)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    mrp = models.DecimalField(
        "MRP", max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Optional list price. When set and higher than the price, the product shows a deal.",
    )
    description = models.TextField()
    image = models.ImageField(upload_to="uploads/products/", blank=True)
    quantity = models.PositiveIntegerField(default=0)
    keywords = models.CharField(max_length=300, blank=True, help_text="Comma-separated words used by search and the recommender.")
    added_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    is_sponsored = models.BooleanField("Sponsored", default=False)
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ProductQuerySet.as_manager()

    class Meta:
        ordering = ["-added_date"]
        constraints = [
            models.CheckConstraint(condition=Q(price__gt=0), name="product_price_gt_0"),
            models.CheckConstraint(condition=Q(quantity__gte=0), name="product_quantity_gte_0"),
            models.CheckConstraint(condition=Q(mrp__isnull=True) | Q(mrp__gte=F("price")), name="product_mrp_gte_price"),
        ]

    def __str__(self) -> str:
        return self.product_name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, f"{self.brand} {self.product_name}", 180)
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        return reverse("catalog:product_detail", args=[self.slug])

    @property
    def is_active(self) -> bool:
        return self.status == Status.ACTIVE and self.category.status == Status.ACTIVE

    @property
    def in_stock(self) -> bool:
        return self.quantity > 0

    @property
    def is_available(self) -> bool:
        """Can a customer buy it right now?"""
        return self.is_active and self.in_stock

    @property
    def low_stock(self) -> bool:
        return 0 < self.quantity <= 5

    @property
    def discount_percent(self) -> int:
        if self.mrp and self.mrp > self.price:
            return int(((self.mrp - self.price) / self.mrp * Decimal(100)).quantize(Decimal("1")))
        return 0

    @property
    def image_url(self) -> str:
        return self.image.url if self.image else static("img/product-placeholder.svg")

    @property
    def keyword_list(self) -> list[str]:
        return [k.strip() for k in self.keywords.split(",") if k.strip()]
