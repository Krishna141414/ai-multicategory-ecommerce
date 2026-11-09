"""Storefront search form (brief: Search Product by product_name, category, min_price, max_price)."""

from decimal import Decimal

from django import forms

from catalog.models import Category, Status

SORT_CHOICES = [
    ("relevance", "Featured"),
    ("price_asc", "Price: low to high"),
    ("price_desc", "Price: high to low"),
    ("newest", "Newest first"),
    ("rating", "Best rated"),
]


class ProductSearchForm(forms.Form):
    product_name = forms.CharField(label="Search", max_length=100, required=False,
                                   widget=forms.TextInput(attrs={"type": "search", "placeholder": "Product, brand or keyword", "autocomplete": "off"}))
    category = forms.ModelChoiceField(label="Category", required=False, to_field_name="slug", empty_label="All categories",
                                      queryset=Category.objects.filter(status=Status.ACTIVE).order_by("category_name"))
    min_price = forms.DecimalField(label="Min price (₹)", required=False, min_value=Decimal("0"), max_digits=10, decimal_places=2,
                                   widget=forms.NumberInput(attrs={"inputmode": "numeric", "placeholder": "0", "step": "1", "min": "0"}))
    max_price = forms.DecimalField(label="Max price (₹)", required=False, min_value=Decimal("0"), max_digits=10, decimal_places=2,
                                   widget=forms.NumberInput(attrs={"inputmode": "numeric", "placeholder": "Any", "step": "1", "min": "0"}))
    in_stock = forms.BooleanField(label="In stock only", required=False)
    sort = forms.ChoiceField(label="Sort by", choices=SORT_CHOICES, required=False)

    error_messages_map = {
        "min_price": "Enter a minimum price of 0 or more, in rupees.",
        "max_price": "Enter a maximum price of 0 or more, in rupees.",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, text in self.error_messages_map.items():
            self.fields[name].error_messages.update({"invalid": text, "min_value": text})

    def clean_product_name(self):
        return " ".join(self.cleaned_data.get("product_name", "").split())

    def clean(self):
        cleaned = super().clean()
        low, high = cleaned.get("min_price"), cleaned.get("max_price")
        if low is not None and high is not None and low > high:
            self.add_error("max_price", "The maximum price must be higher than the minimum price.")
        return cleaned

    def active_filters(self) -> list[tuple[str, str]]:
        """(field name, label) pairs for the filters in use, shown as removable chips."""
        if not self.is_bound or not hasattr(self, "cleaned_data"):
            return []
        data, chips = self.cleaned_data, []
        if data.get("product_name"):
            chips.append(("product_name", f"“{data['product_name']}”"))
        if data.get("category"):
            chips.append(("category", data["category"].category_name))
        if data.get("min_price") is not None:
            chips.append(("min_price", f"From ₹{data['min_price']:,.0f}"))
        if data.get("max_price") is not None:
            chips.append(("max_price", f"Up to ₹{data['max_price']:,.0f}"))
        if data.get("in_stock"):
            chips.append(("in_stock", "In stock"))
        return chips
