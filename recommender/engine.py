"""The AI product recommender: TF-IDF + cosine similarity, run locally with scikit-learn and Pandas.

Pipeline (each step is a small function so the AI Explainer page can show it):

1. collect   `build_frame()`     ProductFeature rows (+ live stock/status) into a Pandas DataFrame
2. clean     `clean_text()`      lowercase, strip HTML, punctuation and number-only tokens
3. combine   `weighted_document()` category + name + brand + description + keywords, with the
                                  name and keywords repeated 3 times and the category twice
4. vectorise `TfidfVectorizer`    one TF-IDF vector per product (words and two-word phrases)
5. compare   `cosine_similarity`  product × product similarity matrix (cached until products change)
6. recommend `Engine.similar()` / `Engine.personalized()` / `popular()` for new customers

Only active, in-stock products are ever recommended. Stock and status are read live on
every call, so a product that sells out drops out at once without rebuilding the matrix.
"""

import re
import threading
from collections import defaultdict
from dataclasses import dataclass

import numpy as np
import pandas as pd
from django.conf import settings
from django.db.models import Avg, Count, Max, Q, Sum
from django.utils import timezone
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from catalog.models import Product
from orders.models import CartItem, OrderStatus
from recommender.features import features_out_of_sync, sync_all_features
from recommender.models import CustomerProductInteraction, ProductFeature

# How many times each field is repeated in the combined document (its weight).
FIELD_WEIGHTS = {"product_name": 3, "keywords": 3, "category": 2, "brand": 1, "description": 1}
MAX_INTEREST_PRODUCTS = 10
INTEREST_VERBS = {"purchase": "bought", "cart": "added", "view": "viewed"}


# ---------------------------------------------------------------- 1-3: collect, clean, combine

def clean_text(text) -> str:
    """Lowercase, drop HTML tags, punctuation and tokens that are only digits; collapse spaces."""
    text = re.sub(r"<[^>]+>", " ", str(text or "").lower())
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return " ".join(token for token in text.split() if not token.isdigit())


def weighted_document(row) -> str:
    """Join the cleaned fields, repeating the important ones so they count for more."""
    parts = []
    for field, weight in FIELD_WEIGHTS.items():
        cleaned = clean_text(row[field])
        if cleaned:
            parts.extend([cleaned] * weight)
    return " ".join(parts)


def build_frame() -> pd.DataFrame:
    """One row per product: the ProductFeature text plus the raw and cleaned documents."""
    rows = ProductFeature.objects.order_by("product_id").values(
        "product_id", "category", "product_name", "brand", "description", "keywords", "price")
    frame = pd.DataFrame.from_records(list(rows), columns=[
        "product_id", "category", "product_name", "brand", "description", "keywords", "price"])
    if frame.empty:
        return frame.assign(raw_text=pd.Series(dtype=str), clean_text=pd.Series(dtype=str), document=pd.Series(dtype=str))
    frame["keywords"] = frame["keywords"].fillna("")
    frame["raw_text"] = frame[["category", "product_name", "brand", "description", "keywords"]].astype(str).agg(" | ".join, axis=1)
    frame["clean_text"] = frame["raw_text"].map(clean_text)
    frame["document"] = frame.apply(weighted_document, axis=1)
    return frame


# ---------------------------------------------------------------- results

@dataclass
class Recommendation:
    """One suggested product with its score and a short human reason."""

    product: Product
    score: float
    score_label: str  # "Similarity" or "Popularity"
    reason: str

    @property
    def percent(self) -> int:
        return round(self.score * 100)


def available_ids() -> set[int]:
    return set(Product.objects.available().values_list("id", flat=True))


def _products(ids: list[int]) -> dict[int, Product]:
    return Product.objects.select_related("category").in_bulk(ids)


def popular(top_n: int = 8, exclude: set[int] | None = None, reason: str = "Popular with shoppers") -> list[Recommendation]:
    """New-customer fallback: most ordered (not cancelled), then best rated. Score = share of the top seller."""
    exclude = exclude or set()
    qs = (Product.objects.available().exclude(id__in=exclude)
          .annotate(sold=Sum("orders__quantity", filter=~Q(orders__order_status=OrderStatus.CANCELLED)),
                    avg_rating=Avg("ratings__rating"), rating_count=Count("ratings", distinct=True))
          .select_related("category").order_by("-sold", "-avg_rating", "-rating_count", "product_name"))
    products = list(qs[:top_n])
    best = max([p.sold or 0 for p in products] + [1])
    return [Recommendation(p, round((p.sold or 0) / best, 4), "Popularity", reason) for p in products]


# ---------------------------------------------------------------- 4-6: vectorise, compare, recommend

class Engine:
    """Holds the fitted TF-IDF model and the similarity matrix for every product."""

    def __init__(self, frame: pd.DataFrame):
        self.frame = frame.reset_index(drop=True)
        self.index = {int(pid): i for i, pid in enumerate(self.frame["product_id"])}
        if len(self.frame):
            self.vectorizer, self.matrix = self._fit(self.frame["document"])
            self.similarity = cosine_similarity(self.matrix)
            self.terms = self.vectorizer.get_feature_names_out()
        else:
            self.vectorizer, self.matrix, self.similarity, self.terms = None, None, np.zeros((0, 0)), np.array([])

    @staticmethod
    def _fit(documents: pd.Series):
        """TF-IDF over words and two-word phrases. min_df=2 keeps only terms at least two products
        share: a word only one product uses can't make it similar to anything, it only dilutes the score."""
        for min_df in (2, 1):  # a tiny catalogue may share no terms at all; then keep every term
            vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), sublinear_tf=True, min_df=min_df)
            try:
                return vectorizer, vectorizer.fit_transform(documents)
            except ValueError:  # "After pruning, no terms remain"
                continue
        raise ValueError("No product text to learn from.")

    # -- helpers
    def knows(self, product_id: int) -> bool:
        return product_id in self.index

    def name_of(self, product_id: int) -> str:
        return self.frame.at[self.index[product_id], "product_name"]

    def top_terms(self, product_id: int, n: int = 12) -> list[tuple[str, float]]:
        """The product's highest-weighted TF-IDF terms (what the engine "sees")."""
        row = self.matrix[self.index[product_id]].tocoo()
        pairs = sorted(zip(row.col, row.data), key=lambda p: -p[1])[:n]
        return [(str(self.terms[c]), round(float(w), 4)) for c, w in pairs]

    def shared_terms(self, a: int, b: int, n: int = 3) -> list[str]:
        """Terms that contribute most to the similarity of two products."""
        overlap = self.matrix[self.index[a]].multiply(self.matrix[self.index[b]]).tocoo()
        pairs = sorted(zip(overlap.col, overlap.data), key=lambda p: -p[1])
        return [str(self.terms[c]) for c, _ in pairs if " " not in str(self.terms[c])][:n]

    def scores_for(self, product_id: int) -> list[tuple[int, float]]:
        """Similarity of every other product to this one, highest first."""
        row = self.similarity[self.index[product_id]]
        order = np.argsort(-row, kind="stable")
        return [(int(self.frame.at[j, "product_id"]), round(float(row[j]), 4)) for j in order
                if int(self.frame.at[j, "product_id"]) != product_id]

    # -- recommendations
    def similar(self, product_id: int, top_n: int | None = None) -> list[Recommendation]:
        """Products most like this one (never itself; only active, in-stock products)."""
        top_n = top_n or settings.RECOMMENDER["TOP_N_SIMILAR"]
        if not self.knows(product_id):
            return []
        allowed = available_ids()
        picked = [(pid, s) for pid, s in self.scores_for(product_id) if pid in allowed and s > 0][:top_n]
        products = _products([pid for pid, _ in picked])
        name = self.name_of(product_id)
        results = []
        for pid, score in picked:
            shared = self.shared_terms(product_id, pid)
            reason = f"Similar to {name}" + (f": {', '.join(shared)}" if shared else "")
            results.append(Recommendation(products[pid], score, "Similarity", reason))
        return results

    def interests(self, customer) -> dict[int, dict]:
        """Weighted interest per product from the customer's views, cart adds and purchases.
        weight = type weight (purchase 3 > cart 2 > view 1) × recency (halves every 14 days)."""
        weights = settings.RECOMMENDER["INTERACTION_WEIGHTS"]
        half_life = settings.RECOMMENDER["HALF_LIFE_DAYS"]
        now = timezone.now()
        result: dict[int, dict] = defaultdict(lambda: {"weight": 0.0, "type": "view", "type_weight": 0.0})
        for row in CustomerProductInteraction.objects.filter(customer=customer).values("product_id", "interaction_type", "interaction_date"):
            age_days = max((now - row["interaction_date"]).total_seconds() / 86400, 0)
            type_weight = weights.get(row["interaction_type"], 1.0)
            entry = result[row["product_id"]]
            entry["weight"] += type_weight * 0.5 ** (age_days / half_life)
            if type_weight > entry["type_weight"]:  # remember the strongest thing they did with it
                entry["type"], entry["type_weight"] = row["interaction_type"], type_weight
        known = {pid: v for pid, v in result.items() if self.knows(pid)}
        top = sorted(known.items(), key=lambda kv: -kv[1]["weight"])[:MAX_INTEREST_PRODUCTS]
        return {pid: {"weight": round(v["weight"], 4), "type": v["type"]} for pid, v in top}

    def personalized(self, customer, top_n: int | None = None) -> list[Recommendation]:
        """'Recommended for you': score_j = Σ wᵢ·sim(i, j) / Σ wᵢ over the customer's interest products i.
        Excludes the interest products, products already in the cart, and unavailable products.
        Customers with no history get popular products instead."""
        top_n = top_n or settings.RECOMMENDER["TOP_N_PERSONAL"]
        interests = self.interests(customer) if customer else {}
        in_cart = set(CartItem.objects.filter(customer=customer).values_list("product_id", flat=True)) if customer else set()
        if not interests:
            return popular(top_n, exclude=in_cart)
        total = sum(v["weight"] for v in interests.values())
        rows = [self.index[pid] for pid in interests]
        w = np.array([interests[pid]["weight"] for pid in interests])
        contributions = self.similarity[rows] * w[:, None]  # one row per interest product
        scores = contributions.sum(axis=0) / total
        allowed = available_ids() - set(interests) - in_cart
        order = np.argsort(-scores, kind="stable")
        picked = [(int(self.frame.at[j, "product_id"]), j) for j in order
                  if int(self.frame.at[j, "product_id"]) in allowed and scores[j] > 0][:top_n]
        products = _products([pid for pid, _ in picked])
        interest_ids = list(interests)
        results = []
        for pid, j in picked:
            source = interest_ids[int(np.argmax(contributions[:, j]))]
            verb = INTEREST_VERBS.get(interests[source]["type"], "viewed")
            reason = f"Because you {verb} {self.name_of(source)}"
            results.append(Recommendation(products[pid], round(float(scores[j]), 4), "Similarity", reason))
        if len(results) < top_n:  # top up with popular products so the shelf is never half empty
            taken = set(interests) | in_cart | {r.product.id for r in results}
            results += popular(top_n - len(results), exclude=taken)
        return results

    def explain(self, product_id: int, top_n: int | None = None, show_scores: int = 12) -> dict:
        """Everything the AI Explainer page shows for one product, step by step."""
        top_n = top_n or settings.RECOMMENDER["TOP_N_SIMILAR"]
        row = self.frame.loc[self.index[product_id]]
        allowed = available_ids()
        scores = self.scores_for(product_id)
        names = dict(zip(self.frame["product_id"].astype(int), self.frame["product_name"]))
        categories = dict(zip(self.frame["product_id"].astype(int), self.frame["category"]))
        return {
            "product_id": product_id,
            "raw": {f: str(row[f]) for f in ("category", "product_name", "brand", "description", "keywords")},
            "clean_text": row["clean_text"],
            "weights": FIELD_WEIGHTS,
            "document_preview": row["document"],
            "vocabulary_size": len(self.terms),
            "product_count": len(self.frame),
            "terms": self.top_terms(product_id),
            "scores": [{"product_id": pid, "name": names[pid], "category": categories[pid], "score": s,
                        "available": pid in allowed, "same_category": categories[pid] == row["category"]}
                       for pid, s in scores[:show_scores]],
            "top": self.similar(product_id, top_n),
        }


# ---------------------------------------------------------------- cache

_lock = threading.Lock()
_cache: dict = {"key": None, "engine": None}


def fingerprint() -> tuple:
    """Changes whenever a product's text, category or price changes (ProductFeature is touched)."""
    stats = ProductFeature.objects.aggregate(n=Count("id"), latest=Max("updated_at"))
    return stats["n"], stats["latest"]


def get_engine(force: bool = False) -> Engine:
    """The fitted engine, rebuilt only when the product features have changed."""
    with _lock:
        if features_out_of_sync():
            sync_all_features()
        key = fingerprint()
        if force or _cache["engine"] is None or _cache["key"] != key:
            _cache["engine"], _cache["key"] = Engine(build_frame()), key
        return _cache["engine"]
