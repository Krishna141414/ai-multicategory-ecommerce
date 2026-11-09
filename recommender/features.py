"""Keep the ProductFeature table (brief: product_id, category, product_name, brand,
description, keywords, price) in step with the catalogue.

Signals update one row when a product or category is saved. `sync_all_features`
rebuilds every row; the engine calls it when the counts drift (for example after
bulk seeding, which skips signals).
"""

from django.db.models.signals import post_save
from django.dispatch import receiver

from catalog.models import Category, Product
from recommender.models import ProductFeature


def feature_values(product: Product) -> dict:
    return {
        "category": product.category.category_name, "product_name": product.product_name, "brand": product.brand,
        "description": product.description, "keywords": product.keywords or "", "price": product.price,
    }


def sync_feature(product: Product) -> ProductFeature:
    """Create or refresh the feature row of one product (only when something changed)."""
    values = feature_values(product)
    feature = ProductFeature.objects.filter(product=product).first()
    if feature is None:
        return ProductFeature.objects.create(product=product, **values)
    if any(getattr(feature, k) != v for k, v in values.items()):
        for k, v in values.items():
            setattr(feature, k, v)
        feature.save()
    return feature


def sync_all_features() -> int:
    """Make ProductFeature match the catalogue exactly. Returns the number of products."""
    products = list(Product.objects.select_related("category"))
    for product in products:
        sync_feature(product)
    ProductFeature.objects.exclude(product__in=products).delete()
    return len(products)


def features_out_of_sync() -> bool:
    return ProductFeature.objects.count() != Product.objects.count()


@receiver(post_save, sender=Product, dispatch_uid="recommender_sync_product_feature")
def _product_saved(sender, instance: Product, raw: bool = False, **kwargs):
    if not raw:  # fixtures load raw rows; the engine resyncs them on first use
        sync_feature(instance)


@receiver(post_save, sender=Category, dispatch_uid="recommender_sync_category_features")
def _category_saved(sender, instance: Category, raw: bool = False, **kwargs):
    if not raw:
        for product in instance.products.select_related("category"):
            sync_feature(product)
