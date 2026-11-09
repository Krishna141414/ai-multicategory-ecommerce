"""AI pages: "View AI Recommended Products" and the AI Explainer (step-by-step view of the engine)."""

from django.http import Http404, JsonResponse
from django.shortcuts import render

from catalog.models import Product
from core.permissions import customer_required, get_customer
from recommender.engine import Engine, get_engine, popular

EXPLAINER_SAMPLE_TERMS = 12


def _interest_rows(engine: Engine, customer) -> list[dict]:
    """The customer's interest products with weight and what they did, strongest first."""
    interests = engine.interests(customer)
    products = Product.objects.select_related("category").in_bulk(list(interests))
    top = max([v["weight"] for v in interests.values()] + [1e-9])
    return [{"product": products[pid], "weight": v["weight"], "share": round(v["weight"] / top * 100), "type": v["type"]}
            for pid, v in interests.items() if pid in products]


@customer_required
def recommended(request):
    """Brief: View AI Recommended Products (personalised; popular picks for new customers)."""
    engine = get_engine()
    interests = _interest_rows(engine, request.customer)
    return render(request, "recommender/recommended.html", {
        "recs": engine.personalized(request.customer), "interests": interests, "is_new": not interests,
    })


def _explainer_product(request, engine: Engine) -> Product:
    """The product chosen in ?product=<id>, or the most popular product to start with."""
    raw = request.GET.get("product", "")
    if raw.isdigit():
        product = Product.objects.active().select_related("category").filter(pk=int(raw)).first()
        if product and engine.knows(product.id):
            return product
    first = popular(1)
    if first:
        return first[0].product
    product = Product.objects.active().select_related("category").first()
    if product is None:
        raise Http404("No products yet")
    return product


def explainer(request):
    """AI Explainer: raw text → cleaned text → TF-IDF terms → cosine scores → top-N, for any product."""
    engine = get_engine()
    product = _explainer_product(request, engine)
    data = engine.explain(product.id)
    top_weight = max([w for _, w in data["terms"]] + [1e-9])
    customer = get_customer(request)
    personal = None
    if customer:
        interests = _interest_rows(engine, customer)
        personal = {"interests": interests[:5], "recs": engine.personalized(customer, top_n=4), "is_new": not interests}
    choices = Product.objects.active().select_related("category").order_by("category__category_name", "product_name")
    return render(request, "recommender/explainer.html", {
        "product": product, "data": data, "personal": personal, "choices": choices,
        "terms": [(t, w, round(w / top_weight * 100)) for t, w in data["terms"]],
    })


def explainer_data(request, product_id: int):
    """The same explanation as JSON (handy for checking the engine without the page)."""
    engine = get_engine()
    if not engine.knows(product_id) or not Product.objects.active().filter(pk=product_id).exists():
        raise Http404("Unknown product")
    data = engine.explain(product_id)
    data["top"] = [{"product_id": r.product.id, "name": r.product.product_name, "category": r.product.category.category_name,
                    "price": str(r.product.price), "score": r.score, "reason": r.reason} for r in data["top"]]
    return JsonResponse(data)
