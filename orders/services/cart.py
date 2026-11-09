"""Cart rules (brief rule 4): several products per cart, quantity never above stock,
zero-stock and hidden products can't be added. Adding logs a `cart` interaction."""

from dataclasses import dataclass, field
from decimal import Decimal

from django.db import transaction

from catalog.models import Product
from orders.models import CartItem
from recommender.interactions import CART, log_interaction

MAX_PER_LINE = 10  # a sensible per-item limit for a demo store


class CartError(Exception):
    """A cart change that isn't allowed; the message is shown to the customer."""


@dataclass
class CartLine:
    item: CartItem
    product: Product
    quantity: int
    line_total: Decimal
    problem: str = ""  # why this line can't be checked out right now (empty when fine)

    @property
    def max_quantity(self) -> int:
        return max(1, min(self.product.quantity, MAX_PER_LINE))


@dataclass
class CartSummary:
    lines: list[CartLine] = field(default_factory=list)
    total: Decimal = Decimal("0")
    count: int = 0

    @property
    def has_problems(self) -> bool:
        return any(line.problem for line in self.lines)

    @property
    def is_empty(self) -> bool:
        return not self.lines


def line_problem(product: Product, quantity: int) -> str:
    if not product.is_active:
        return "No longer available. Remove it to check out."
    if product.quantity == 0:
        return "Out of stock. Remove it to check out."
    if quantity > product.quantity:
        return f"Only {product.quantity} left. Lower the quantity to check out."
    return ""


def get_cart(customer) -> CartSummary:
    """Brief: View Cart. Lines with live prices, the order total and any stock problems."""
    summary = CartSummary()
    items = CartItem.objects.filter(customer=customer).select_related("product__category").order_by("added_date", "id")
    for item in items:
        product = item.product
        line = CartLine(item=item, product=product, quantity=item.quantity, line_total=product.price * item.quantity,
                        problem=line_problem(product, item.quantity))
        summary.lines.append(line)
        summary.total += line.line_total
        summary.count += item.quantity
    return summary


def cart_count(customer) -> int:
    return sum(CartItem.objects.filter(customer=customer).values_list("quantity", flat=True))


def _check_quantity(product: Product, quantity: int) -> None:
    if quantity < 1:
        raise CartError("Choose a quantity of at least 1.")
    if not product.is_active:
        raise CartError("This product is no longer sold.")
    if product.quantity == 0:
        raise CartError(f"“{product.product_name}” is out of stock.")
    if quantity > product.quantity:
        raise CartError(f"Only {product.quantity} of “{product.product_name}” left in stock.")
    if quantity > MAX_PER_LINE:
        raise CartError(f"You can buy up to {MAX_PER_LINE} of one item per order.")


@transaction.atomic
def add_to_cart(customer, product: Product, quantity: int = 1) -> CartItem:
    """Brief: Add to Cart. Adds to an existing line; the line total can't exceed stock."""
    product = Product.objects.select_related("category").get(pk=product.pk)  # fresh stock figure
    item = CartItem.objects.filter(customer=customer, product=product).first()
    new_quantity = (item.quantity if item else 0) + quantity
    if item and quantity >= 1 and new_quantity > product.quantity:
        raise CartError(f"You already have {item.quantity} in your cart and only {product.quantity} are in stock.")
    _check_quantity(product, new_quantity)
    if item:
        item.quantity = new_quantity
        item.save(update_fields=["quantity"])
    else:
        item = CartItem.objects.create(customer=customer, product=product, quantity=new_quantity)
    log_interaction(customer, product, CART)
    return item


@transaction.atomic
def update_quantity(customer, item_id: int, quantity: int) -> CartItem:
    """Brief: Update Cart Quantity (1 to available stock)."""
    item = CartItem.objects.select_related("product__category").filter(customer=customer, pk=item_id).first()
    if item is None:
        raise CartError("That item is no longer in your cart.")
    _check_quantity(item.product, quantity)
    item.quantity = quantity
    item.save(update_fields=["quantity"])
    return item


def remove_item(customer, item_id: int) -> str:
    """Brief: Remove from Cart. Returns the product name for the confirmation message."""
    item = CartItem.objects.select_related("product").filter(customer=customer, pk=item_id).first()
    if item is None:
        raise CartError("That item is no longer in your cart.")
    name = item.product.product_name
    item.delete()
    return name
