from django.apps import AppConfig


class RecommenderConfig(AppConfig):
    name = "recommender"

    def ready(self):
        from recommender import features  # noqa: F401  (registers the ProductFeature sync signals)
