"""Template helpers: Indian rupee formatting and form-field styling."""

from decimal import Decimal, InvalidOperation

from django import template

register = template.Library()


def indian_grouping(whole: str) -> str:
    """'12499999' -> '1,24,99,999' (Indian digit grouping)."""
    if len(whole) <= 3:
        return whole
    head, tail = whole[:-3], whole[-3:]
    groups = []
    while len(head) > 2:
        groups.insert(0, head[-2:])
        head = head[:-2]
    if head:
        groups.insert(0, head)
    return ",".join(groups + [tail])


@register.filter
def inr(value, decimals: int = 2) -> str:
    """Format a number as rupees: 124999.5 -> '₹1,24,999.50'. Use |inr:0 to drop paise."""
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return ""
    sign = "-" if amount < 0 else ""
    amount = abs(amount).quantize(Decimal(1) if int(decimals) == 0 else Decimal("0.01"))
    whole, _, paise = f"{amount:f}".partition(".")
    text = indian_grouping(whole)
    return f"{sign}₹{text}.{paise}" if paise else f"{sign}₹{text}"


@register.filter
def add_class(bound_field, css: str):
    """Render a form field with extra CSS classes (adds is-invalid when it has errors)."""
    classes = css + (" is-invalid" if bound_field.errors else "")
    attrs = {"class": classes}
    if bound_field.errors:
        attrs["aria-invalid"] = "true"
        attrs["aria-describedby"] = f"{bound_field.auto_id}-error"
    elif bound_field.help_text:
        attrs["aria-describedby"] = f"{bound_field.auto_id}-help"
    return bound_field.as_widget(attrs=attrs)


@register.filter
def star_list(value) -> list[str]:
    """5 star states for a rating or an average: 4.5 -> full ×4 + half; 3.2 -> full ×3 + empty ×2."""
    try:
        value = float(value or 0)
    except (TypeError, ValueError):
        value = 0.0
    stars = []
    for i in range(1, 6):
        if value >= i - 0.25:
            stars.append("full")
        elif value >= i - 0.75:
            stars.append("half")
        else:
            stars.append("empty")
    return stars


@register.filter
def get_item(mapping, key):
    """Dictionary lookup in templates: {{ counts|get_item:status }}."""
    try:
        return mapping.get(key)
    except AttributeError:
        return None
