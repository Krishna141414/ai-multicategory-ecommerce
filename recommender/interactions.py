"""Record what customers do with products (brief: CustomerProductInteraction).

These rows tell the recommender what a customer is interested in: views < cart < purchases.
"""

from datetime import timedelta

from django.utils import timezone

from recommender.models import CustomerProductInteraction

VIEW = CustomerProductInteraction.Type.VIEW
CART = CustomerProductInteraction.Type.CART
PURCHASE = CustomerProductInteraction.Type.PURCHASE

# A refresh or a quick back-and-forth should not count as several separate views.
VIEW_DEDUPE_WINDOW = timedelta(minutes=10)


def log_interaction(customer, product, interaction_type: str) -> CustomerProductInteraction | None:
    """Store one interaction. Repeated views within 10 minutes are counted once."""
    if customer is None or product is None:
        return None
    if interaction_type == VIEW:
        recent = CustomerProductInteraction.objects.filter(
            customer=customer, product=product, interaction_type=VIEW,
            interaction_date__gte=timezone.now() - VIEW_DEDUPE_WINDOW).exists()
        if recent:
            return None
    return CustomerProductInteraction.objects.create(customer=customer, product=product, interaction_type=interaction_type)
