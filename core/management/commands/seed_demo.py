"""Load demo data: categories, products, customers, orders, reviews, messages, interactions."""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core import demo


class Command(BaseCommand):
    help = "Load the demo store data (safe to run more than once)."

    @transaction.atomic
    def handle(self, *args, **options):
        try:
            categories, products = demo.seed_catalog()
            customers = demo.seed_customers()
            orders = demo.seed_orders()
            demo.seed_carts_and_views()
            conversations = demo.seed_conversations()
        except ValueError as exc:
            raise CommandError(str(exc)) from exc
        self.stdout.write(self.style.SUCCESS(
            f"Catalogue: {categories} categories, {products} products. Customers: {len(customers)}. "
            f"Orders: {orders}. Conversations: {conversations}."))
