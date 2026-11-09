"""python manage.py build_recommender — sync ProductFeature and rebuild the TF-IDF / similarity matrix now."""

import time

from django.core.management.base import BaseCommand

from recommender.engine import get_engine
from recommender.features import sync_all_features


class Command(BaseCommand):
    help = "Sync the ProductFeature table and rebuild the recommender (TF-IDF + cosine similarity)."

    def handle(self, *args, **options):
        started = time.perf_counter()
        products = sync_all_features()
        engine = get_engine(force=True)
        seconds = time.perf_counter() - started
        self.stdout.write(self.style.SUCCESS(
            f"Recommender built: {products} products, {len(engine.terms)} TF-IDF terms, "
            f"similarity matrix {engine.similarity.shape[0]} x {engine.similarity.shape[1]}, {seconds:.2f} s."))
