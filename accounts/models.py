"""Customer profile: the brief's customer fields, linked one-to-one to Django's User.

The password lives on `User` (Django hashes it); everything else the brief lists
for a customer lives here.
"""

from django.conf import settings
from django.db import models
from django.db.models.functions import Lower
from django.urls import reverse
from django.utils import timezone


class Customer(models.Model):
    """A shopper. Brief fields: id, name, email, mobile_number, address, registered_date, status."""

    class Status(models.TextChoices):
        ACTIVE = "Active", "Active"
        INACTIVE = "Inactive", "Inactive"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="customer")
    name = models.CharField(max_length=120)
    email = models.EmailField(max_length=254, unique=True)
    mobile_number = models.CharField(max_length=15)
    address = models.TextField()
    registered_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        ordering = ["-registered_date"]
        constraints = [
            models.UniqueConstraint(Lower("email"), name="unique_customer_email_ci"),
        ]

    def __str__(self) -> str:
        return f"{self.name} <{self.email}>"

    def save(self, *args, **kwargs):
        self.email = self.email.strip().lower()
        super().save(*args, **kwargs)

    @property
    def is_active(self) -> bool:
        return self.status == self.Status.ACTIVE

    @property
    def first_name(self) -> str:
        return self.name.split()[0] if self.name else ""

    def get_admin_url(self) -> str:
        return reverse("adminpanel:customer_detail", args=[self.pk])
