"""Admin forms. Every rule from the brief is checked here on the server as well as in the database."""

from decimal import Decimal

from django import forms

from catalog.models import Category, Product, Status
from orders.models import OrderStatus
from orders.services.status import next_statuses

MAX_IMAGE_BYTES = 3 * 1024 * 1024


class CategoryForm(forms.ModelForm):
    """Brief: Add / Update Category (category_name, description, status)."""

    class Meta:
        model = Category
        fields = ["category_name", "description", "status"]
        labels = {"category_name": "Category name"}
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}

    def clean_category_name(self):
        name = " ".join(self.cleaned_data["category_name"].split())
        if len(name) < 2:
            raise forms.ValidationError("Enter a category name.")
        clash = Category.objects.filter(category_name__iexact=name).exclude(pk=self.instance.pk)
        if clash.exists():
            raise forms.ValidationError("A category with this name already exists.")
        return name


class ProductForm(forms.ModelForm):
    """Brief: Add / Update Product (category_id, product_name, brand, price, description, image,
    quantity, keywords, status) plus MRP and the sponsored toggle."""

    class Meta:
        model = Product
        fields = ["category", "product_name", "brand", "price", "mrp", "quantity", "description", "keywords",
                  "image", "status", "is_sponsored"]
        labels = {"product_name": "Product name", "price": "Price (₹)", "mrp": "MRP (₹, optional)",
                  "quantity": "Quantity in stock", "is_sponsored": "Show in the sponsored deals strip"}
        error_messages = {
            "quantity": {"min_value": "Quantity can’t be negative.", "invalid": "Enter a whole number."},
            "price": {"invalid": "Enter a price in rupees, for example 2499 or 2499.50."},
        }
        help_texts = {"keywords": "Comma-separated, e.g. wireless earbuds, bluetooth, noise cancelling. Used by search and the recommender."}
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
            "price": forms.NumberInput(attrs={"step": "0.01", "min": "0.01", "inputmode": "decimal"}),
            "mrp": forms.NumberInput(attrs={"step": "0.01", "min": "0.01", "inputmode": "decimal"}),
            "quantity": forms.NumberInput(attrs={"min": "0", "step": "1", "inputmode": "numeric"}),
            "image": forms.ClearableFileInput(attrs={"accept": "image/jpeg,image/png,image/webp"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categories = Category.objects.filter(status=Status.ACTIVE)
        if self.instance.pk:
            categories = categories | Category.objects.filter(pk=self.instance.category_id)
        self.fields["category"].queryset = categories.distinct().order_by("category_name")
        self.fields["category"].empty_label = "Choose a category"

    def clean_product_name(self):
        name = " ".join(self.cleaned_data["product_name"].split())
        if len(name) < 2:
            raise forms.ValidationError("Enter the product name.")
        return name

    def clean_brand(self):
        return " ".join(self.cleaned_data["brand"].split())

    def clean_price(self):
        price = self.cleaned_data["price"]
        if price is None or price <= 0:
            raise forms.ValidationError("Price must be greater than zero.")
        return price

    def clean_quantity(self):
        qty = self.cleaned_data["quantity"]
        if qty is None or qty < 0:
            raise forms.ValidationError("Quantity can’t be negative.")
        return qty

    def clean_keywords(self):
        words = [w.strip().lower() for w in self.cleaned_data.get("keywords", "").split(",") if w.strip()]
        return ", ".join(dict.fromkeys(words))  # tidy and de-duplicate, keep order

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if image and hasattr(image, "size") and image.size > MAX_IMAGE_BYTES:
            raise forms.ValidationError("Images must be 3 MB or smaller.")
        return image

    def clean(self):
        cleaned = super().clean()
        price, mrp = cleaned.get("price"), cleaned.get("mrp")
        if price and mrp is not None and mrp < price:
            self.add_error("mrp", "MRP can't be lower than the price. Leave it empty if there is no discount.")
        if mrp is not None and mrp <= Decimal(0):
            self.add_error("mrp", "MRP must be greater than zero.")
        return cleaned


class OrderStatusForm(forms.Form):
    """Brief: Update Order Status. Only the moves allowed from the current status are offered."""

    order_status = forms.ChoiceField(label="New status")

    def __init__(self, *args, current_status: str = OrderStatus.PENDING, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["order_status"].choices = [(s, s) for s in next_statuses(current_status)]
