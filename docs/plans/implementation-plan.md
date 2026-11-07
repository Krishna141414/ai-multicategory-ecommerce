# AI Multi-Category E-Commerce: Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans (the owner asked for in-session, phase-by-phase execution). Steps use checkbox (`- [ ]`) syntax. Phase numbers match `BUILD_PROMPT.md`.

**Goal:** A locally-running Django store with 10 categories, custom admin and customer sides, a TF-IDF + cosine-similarity recommender, and a Playwright + Pytest suite whose results land on an admin "Test Reports" page.

**Architecture:** One Django project (`config/`) with 9 focused apps. Views stay thin and call service modules (`orders/services/*.py`, `recommender/engine.py`, `messaging/services.py`, `reviews/services.py`) that hold the business rules. Shop data lives in `db.sqlite3`; test-run data lives in a second SQLite file (`reports.sqlite3`) reached through a DB router, so test runs never touch shop data.

**Tech Stack:** Python 3.14, Django 6.1.3, SQLite, Bootstrap 5.3.8 (custom design system on top), vanilla JS + GSAP 3.15 / ScrollTrigger / Lenis 1.3 (all local), scikit-learn 1.9.1, pandas 3.1.1, pytest 9.2 + pytest-django 4.14 + pytest-playwright 0.10 + pytest-html 4.2.

**Spec:** `docs/PROJECT_BRIEF.md` (what), `CLAUDE.md` (rules), `BUILD_PROMPT.md` (order). Library facts: `docs/research/library-notes.md`.

## Global Constraints
- Brief field names are the contract: never remove/rename them (extra fields allowed).
- Category names exactly: Electronics; Fashion and Clothing; Home and Furniture; Books and Stationery; Beauty and Personal Care; Sports and Fitness; Mobile Phones and Accessories; Computers and Laptops; Toys and Games; Kitchen and Home Appliances.
- Order statuses exactly: Pending, Confirmed, Shipped, Delivered, Cancelled.
- Currency ₹ (Indian grouping, e.g. ₹1,24,999.00). Brands fictional.
- No CDN at runtime; all vendor assets under `static/vendor/`. No paid APIs, no LLM.
- `price > 0`, `quantity >= 0` enforced by DB `CheckConstraint` AND form validation.
- Every form posts with CSRF; every view is role-guarded (customer-only / admin-only / public).
- Secrets only from `.env`. Commands must run in Windows PowerShell.
- Tests: Playwright sync API, `live_server`, separate test DB file, locators only `get_by_role/label/text/test_id`, no `time.sleep`.

## Review Focus
1. **Double submit / two tabs on "Place order"** → exactly one set of order rows. Test: `tests/unit/test_checkout_service.py::test_resubmit_same_key_returns_same_order`.
2. **Stock bought by someone else between add-to-cart and submit** → clear error, no partial orders, no stock change. Test: `test_submit_rolls_back_when_one_item_short`.
3. **Product deactivated/deleted while in a cart** → cart flags it "No longer available", submit refuses until removed. Test: `test_submit_rejects_inactive_product`.
4. **Customer deactivated while logged in** → next request logs them out with a message. Test: `tests/unit/test_auth.py::test_deactivated_session_is_logged_out`.
5. **Bad search input** (min > max, letters, negative) → form error shown, page renders 200, not 500. Test: `tests/unit/test_search.py::test_invalid_price_range_shows_error`.
(Also pinned: email uniqueness is case-insensitive — `test_duplicate_email_case_insensitive`.)

---

## File structure

```
config/            settings.py (reads .env), urls.py, db_router.py (testreports → "reports"), wsgi.py
core/              home view, base templates, context_processors.py (cart_count, nav_categories),
                   permissions.py (customer_required, admin_required, CustomerRequiredMixin, AdminRequiredMixin),
                   middleware.py (ActiveCustomerMiddleware), templatetags/shop_tags.py (inr, stars),
                   management/commands/reset_demo.py
accounts/          models.py (Customer), backends.py (EmailBackend), forms.py, views.py, urls.py,
                   management/commands/create_default_admin.py
catalog/           models.py (Category, Product), forms.py (ProductSearchForm), services.py (search_products,
                   active_products), views.py, urls.py, seed_data.py, management/commands/seed_demo.py
orders/            models.py (CartItem, Order, Payment), services/cart.py, services/checkout.py,
                   services/payment.py, emails.py, forms.py, views.py, urls.py, templates/emails/
reviews/           models.py (Rating, Review), services.py, forms.py, views.py, urls.py
messaging/         models.py (Message), services.py, forms.py, views.py (customer side), urls.py
recommender/       models.py (ProductFeature, CustomerProductInteraction), engine.py, interactions.py,
                   signals.py (sync ProductFeature), views.py (recommended page, explainer, explainer JSON),
                   urls.py, management/commands/build_recommender.py
adminpanel/        forms.py, views/ (dashboard.py, categories.py, products.py, customers.py, orders.py,
                   reviews.py, queries.py, test_reports.py), urls.py   — mounted at /manage/
testreports/       models.py (TestCase, TestExecution, TestSummary), services.py (record_run),
                   management/commands/record_test_run.py, sync_test_catalog.py
templates/         base.html, partials/, store pages, adminpanel/ pages
static/            css/tokens.css, css/store.css, css/admin.css, js/*.js, vendor/, fonts/, img/
tests/             conftest.py, catalog.py (TC catalogue), factories.py, pages/, admin/, customer/, ai/, e2e/, unit/
run_tests.ps1, pytest.ini, requirements.txt, .env.example
```

## Key data model (brief fields **bold**; extras plain)
- `Customer`: user (1:1 User), **name, email** (unique, stored lowercased + `UniqueConstraint(Lower("email"))`), **mobile_number, address, registered_date, status** (Active/Inactive, default Active). Password lives on `User` (hashed).
- `Category`: **id, category_name** (unique), **description, status** (Active/Inactive), **created_date**, slug.
- `Product`: **id, category** (FK PROTECT → `category_id`), **product_name, brand, price** (Decimal, CHECK > 0), **description, image, quantity** (CHECK ≥ 0), **keywords, added_date, status** (Active/Inactive), is_sponsored, updated_at, slug.
- `CartItem`: **id, customer, product, quantity** (≥ 1), **added_date**; unique (customer, product).
- `Order` (one row per item): **id, order_id** (e.g. `ORD-20261107-7K3Q`, indexed), **customer, product** (FK PROTECT), product_name (snapshot), **quantity, price** (snapshot), **amount** (= price × quantity), **order_date, order_status**, checkout_key.
- `Payment`: **id, order_id, customer, total_amount, payment_method** (Card/UPI/Net Banking), **payment_status** (Success/Failed), **payment_date**.
- `Rating`: **id, product, customer, rating** (1–5, CHECK), **posted_date**; unique (product, customer).
- `Review`: **id, product, customer, review, posted_date**; unique (product, customer) (editable).
- `Message`: **id, conversation_id** (`CNV-xxxxxxxx`), **sender** (→ `sender_id`), **sender_type** (admin/customer), **receiver** (→ `receiver_id`), **receiver_type, parent_message** (→ `parent_message_id`, NULL starts a conversation), **subject, message, posted_date, status** (Unread/Read).
- `ProductFeature`: **id, product** (1:1), **category, product_name, brand, description, keywords, price**.
- `CustomerProductInteraction`: **id, customer, product, interaction_type** (view/cart/purchase), **interaction_date**.
- Reports DB: `TestCase` (**id** = "TC-ADM-01", **test_name, module, test_description, expected_result**); `TestSummary` (**id, execution_date, total_tests, passed_tests, failed_tests, skipped_tests, total_execution_time, report_path**); `TestExecution` (**id, test_case_id, execution_date, actual_result, status, execution_time, screenshot_path**, summary FK).

---

## Phase 2 — Scaffold, models, seed

### Task 2.1: Project + settings
**Files:** `manage.py`, `config/*`, every app's `apps.py`.
- [ ] `settings.py`: load `.env` with python-dotenv; `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS` from env; `DATABASES = {"default": db.sqlite3 with OPTIONS {"transaction_mode": "IMMEDIATE"} and TEST NAME test_db.sqlite3, "reports": reports.sqlite3 (TEST NAME test_reports.sqlite3)}`; `DATABASE_ROUTERS=["config.db_router.ReportsRouter"]`; `AUTHENTICATION_BACKENDS=["accounts.backends.EmailBackend", "django.contrib.auth.backends.ModelBackend"]`; email: `EMAIL_MODE=file` → filebased backend at `BASE_DIR/"sent_emails"`; `MEDIA_ROOT=BASE_DIR/"media"`; `LOGIN_URL="accounts:login"`; `TIME_ZONE="Asia/Kolkata"`.
- [ ] `ReportsRouter`: app_label `testreports` → "reports" for read/write/migrate; everything else never migrates on "reports".
- [ ] Verify: `python manage.py check` → "System check identified no issues".

### Task 2.2: Models + migrations
- [ ] Implement the data model above. Constraints: `CheckConstraint(condition=Q(price__gt=0))`, `Q(quantity__gte=0)`, rating `Q(rating__gte=1, rating__lte=5)`, cart `Q(quantity__gte=1)`.
- [ ] Test `tests/unit/test_models.py`: `test_price_must_be_positive` (IntegrityError on price=0), `test_quantity_cannot_be_negative`, `test_order_amount_is_price_times_quantity` (`Order.save()` sets amount), `test_duplicate_email_case_insensitive`.
- [ ] Verify: `python manage.py makemigrations && python manage.py migrate && python manage.py migrate --database=reports`; `pytest tests/unit/test_models.py` PASS.

### Task 2.3: Vendor assets (local)
- [ ] Download Bootstrap 5.3.8 css+bundle js, GSAP 3.15.1 + ScrollTrigger, Lenis 1.3.27, Bootstrap Icons 1.13.2 (css + woff2), chosen fonts (woff2) into `static/vendor/` and `static/fonts/`. Record versions/licences in `static/vendor/README.md`.
- [ ] Verify: `rg -n "https?://(cdn|unpkg|fonts\.g)" templates static/css static/js` → no matches.

### Task 2.4–2.6: Seed + commands
**Produces:** `python manage.py create_default_admin`, `seed_demo`, `reset_demo`, data in `catalog/seed_data.py` (`CATEGORIES: list[dict]`, `PRODUCTS: list[dict]` with `category, product_name, brand, price, quantity, description, keywords, image, is_sponsored`).
- [ ] 10 categories, 10–12 products each (≈110), fictional brands, a few `quantity=0`, ~8 sponsored. Descriptions humanized.
- [ ] Images: Openverse/Wikimedia CC0/CC-BY into `media/products/`, credits in `docs/IMAGE_CREDITS.md`; designed placeholders where nothing fits.
- [ ] `seed_demo` is idempotent (`update_or_create` by slug); also 4 demo customers, past orders (mixed statuses), payments, ratings, reviews, 2 conversations, interactions.
- [ ] `reset_demo`: flush shop data (not reports DB), re-run `create_default_admin` + `seed_demo` + `build_recommender`.
- [ ] Verify: run all three twice; `shell -c` counts: 10 categories, ≥100 products, 4 customers.

## Phase 3 — Auth & roles
**Produces:** `core.permissions.customer_required(view)`, `admin_required(view)`, mixins; `accounts.backends.EmailBackend.authenticate(request, email=None, password=None)`; `accounts.services.login_error_for(email, password) -> str | None` (returns the deactivated message only when the password is correct).
- [ ] Registration form: name, email, mobile_number (10 digits, starts 6–9), password + confirm (Django validators), address. Creates User(username=email) + Customer(status=Active), logs in.
- [ ] Customer login (email + password). Messages: invalid → "Email or password is incorrect."; inactive with correct password → "Your account has been deactivated. Please contact support."
- [ ] Admin login at `/manage/login/` (username + password, `is_staff` required).
- [ ] Guards: customer pages redirect anonymous users to login; staff hitting customer-only pages → 403 page; customers hitting `/manage/*` → 403.
- [ ] `ActiveCustomerMiddleware`: a logged-in customer whose status is Inactive is logged out on the next request.
- [ ] Profile view/update (email stays unique).
- [ ] Tests `tests/unit/test_auth.py`: `test_register_creates_active_customer`, `test_password_is_hashed`, `test_duplicate_email_case_insensitive`, `test_inactive_customer_cannot_login`, `test_deactivated_session_is_logged_out`, `test_customer_cannot_open_admin`, `test_admin_cannot_use_cart`.

## Phase 4 — Admin panel (`/manage/`)
- [ ] Dashboard: total_customers, total_categories, total_products (active), total_orders (distinct order_id), total_sales (sum amount of orders with a Success payment, excluding Cancelled) + recent orders + 14-day orders/sales chart (inline SVG, no chart lib).
- [ ] Categories CRUD with search. **Delete rule (decision):** blocked with a clear message while the category has products; empty categories are deleted after a confirm dialog.
- [ ] Products CRUD: list with filters (category, status, stock, sponsored, search), image upload, sponsored toggle (POST, inline). Delete → `catalog.services.delete_product(product) -> str` returns `"deleted"` or `"deactivated"` (soft delete when any Order references it).
- [ ] Customers: list/detail; activate/deactivate (POST).
- [ ] Orders: grouped by order_id, expandable rows; status update via `orders.services.checkout.set_order_status(order_id: str, new_status: str) -> None` (allowed transitions: Pending→Confirmed|Cancelled, Confirmed→Shipped|Cancelled, Shipped→Delivered; Cancelled restores stock with `F()`; raises `OrderStatusError` otherwise).
- [ ] Ratings & reviews list (product, customer, rating, review, date).
- [ ] Queries: inbox (conversations with last message + unread badge), post new query to a chosen customer, reply, full thread.
- [ ] Tests `tests/unit/test_admin_services.py`: `test_delete_product_with_orders_soft_deletes`, `test_delete_product_without_orders_hard_deletes`, `test_cancel_restores_stock`, `test_invalid_transition_rejected`, `test_category_with_products_cannot_be_deleted`.

## Phase 5 — Catalogue
**Produces:** `catalog.forms.ProductSearchForm` (product_name, category, min_price, max_price, sort ∈ {relevance, price_asc, price_desc, newest, rating}); `catalog.services.search_products(cleaned: dict) -> QuerySet[Product]` (active products in active categories, annotated `avg_rating`, `rating_count`).
- [ ] Category grid page; product listing with filters + sort + pagination (12/page); empty state.
- [ ] Product detail: all brief fields, average rating + count, reviews, out-of-stock state, quantity selector capped at stock; logs a `view` interaction for logged-in customers.
- [ ] Tests `tests/unit/test_search.py`: `test_search_by_name_icontains`, `test_search_by_category`, `test_search_by_price_range`, `test_combined_filters`, `test_invalid_price_range_shows_error`, `test_inactive_products_hidden`.

## Phase 6 — Cart, checkout, payment
**Interfaces (Produces):**
- `orders.services.cart`: `add_to_cart(customer, product, quantity=1) -> CartItem`; `update_quantity(customer, item_id, quantity) -> CartItem`; `remove_item(customer, item_id) -> None`; `get_cart(customer) -> CartSummary` (`items`, `total: Decimal`, `count: int`, `has_problems: bool`). All raise `CartError(message)`.
- `orders.services.checkout`: `submit_cart(customer, checkout_key: str) -> str` (order_id); `order_rows(order_id) -> QuerySet[Order]`; `order_total(order_id) -> Decimal`; `set_order_status(...)` (Phase 4).
- `orders.services.payment`: `pay(customer, order_id, method: str, outcome: str) -> PaymentResult(payment, already_paid: bool)`.
- `orders.emails.send_order_email(order_id) -> None`.

**submit_cart algorithm (decided):**
1. If an Order with this `checkout_key` exists for the customer → return its order_id (double-click / resubmit guard).
2. `with transaction.atomic()` (SQLite IMMEDIATE = write lock): load cart items; reject empty cart / inactive product / qty > stock; lock products with `select_for_update()`; for each item `Product.objects.filter(pk, quantity__gte=q).update(quantity=F("quantity")-q)` — 0 rows → raise `CheckoutError` (rolls back everything).
3. Cancel the customer's older *unpaid Pending* order groups (restore their stock) so abandoned checkouts don't hold stock forever.
4. Create one `Order` per item with shared new `order_id`, snapshot name/price, amount, status Pending, checkout_key.
5. Cart is **not** cleared here.

**pay algorithm:** if a Success payment exists for order_id → `already_paid=True`, no new rows. Else create Payment(total = order_total); on Success: set rows Pending→Confirmed, clear the customer's cart items for those products, log `purchase` interactions, send email (via `transaction.on_commit`). On Failure: Payment(Failed) only; orders stay Pending; retry allowed.

- [ ] Views: cart (update/remove forms, live totals via fetch + server re-render fallback), checkout review (hidden `checkout_key` uuid per render), payment (method radios + "Simulate result: Success / Failure"), confirmation, order history (grouped), order detail.
- [ ] Tests `tests/unit/test_checkout_service.py`: `test_submit_creates_one_row_per_item_with_shared_order_id`, `test_amount_and_total`, `test_stock_reserved_on_submit`, `test_submit_rolls_back_when_one_item_short`, `test_submit_rejects_inactive_product`, `test_resubmit_same_key_returns_same_order`, `test_payment_success_confirms_and_clears_cart_and_emails`, `test_payment_failure_keeps_pending`, `test_pay_twice_is_idempotent`, `test_cancel_restores_stock`, `test_add_to_cart_blocks_zero_stock`, `test_cart_qty_cannot_exceed_stock`.

## Phase 7 — Reviews & queries (customer)
- `reviews.services.can_review(customer, product) -> bool` (has an Order for product with status Confirmed/Shipped/Delivered); `save_rating(customer, product, value) -> Rating` (update_or_create); `save_review(customer, product, text) -> Review`.
- `messaging.services`: `start_conversation(sender, sender_type, receiver, receiver_type, subject, message) -> Message`; `reply(parent: Message, sender, sender_type, message) -> Message` (same conversation_id, receiver = other party); `conversations_for(user) -> list[ConversationSummary]`; `thread(conversation_id, user) -> list[Message]` (raises `PermissionDenied` when a customer isn't a participant); `mark_read(conversation_id, user)`.
- Customer-posted queries go to the default admin (`User.objects.filter(is_staff=True).order_by("id").first()`).
- [ ] Tests: `test_cannot_review_without_purchase`, `test_rating_is_updated_not_duplicated`, `test_new_conversation_has_null_parent`, `test_reply_reuses_conversation_id`, `test_customer_cannot_see_other_thread`.

## Phase 8 — Recommender
**Interfaces (Produces) in `recommender/engine.py`:**
- `clean_text(text: str) -> str` — lowercase, strip HTML/punctuation/digits-only tokens, collapse spaces.
- `build_frame() -> pd.DataFrame` — from ProductFeature joined with Product (status, quantity, image, slug); columns `product_id, category, product_name, brand, description, keywords, price, is_available, raw_text, clean_text`.
- Weighted document: name ×3, category ×2, keywords ×3, brand ×1, description ×1 (repeat tokens).
- `class Engine`: `fit(df)`; `similar(product_id, top_n=6) -> list[Recommendation]`; `personalized(customer, top_n=8) -> list[Recommendation]`; `top_terms(product_id, n=12) -> list[tuple[str, float]]`; `explain(product_id, top_n=6) -> dict` (raw, cleaned, terms, scores, top).
- `Recommendation` dataclass: `product`, `score: float`, `score_label: str` ("Similarity"/"Popularity"), `reason: str`.
- `get_engine() -> Engine` — module cache keyed by fingerprint `(ProductFeature count, max Product.updated_at)`; rebuilt automatically when products change. `build_recommender` command forces a rebuild and prints stats.
- Vectorizer: `TfidfVectorizer(stop_words="english", ngram_range=(1, 2), sublinear_tf=True)`; `cosine_similarity(X)`.
- Personalised: interests from interactions; weight purchase 3, cart 2, view 1; recency × `0.5 ** (age_days / 14)`; up to 10 most-weighted interest products; score_j = Σ wᵢ·sim(i,j) / Σ wᵢ; exclude interest products, unavailable products and products already in cart; reason = "Because you {viewed|added|bought} {name}" from the largest contributor.
- New customer fallback: most ordered (non-cancelled qty) then best rated, available only; score = normalised popularity, label "Popularity", reason "Popular with shoppers".
- [ ] Pages: product page "Similar products"; home "Recommended for you"; `/recommendations/`; `/ai/explainer/?product=<id>` with steps + personal panel; JSON endpoint `/ai/explainer/data/<id>/`.
- [ ] Tests `tests/unit/test_engine.py`: `test_feature_matrix_shape`, `test_top_terms_include_keywords`, `test_similar_excludes_self`, `test_similar_excludes_inactive_and_out_of_stock`, `test_similar_same_category_first`, `test_scores_sorted_desc`, `test_personalized_excludes_interests`, `test_new_customer_gets_popular`.
- [ ] Gate: `docs/research/recommender-check.md` with 5 sample products' top-5.

## Phase 9 — Design pass
Apply `docs/DESIGN_SYSTEM.md`; homepage per `docs/plans/pages.md`; sponsored strip (`static/js/sponsored.js`: CSS transform marquee driven by GSAP ticker, pause on hover/focus, prev/next buttons, quick-view card on hover/focus/tap, Esc closes); micro-interactions; admin skin; Playwright MCP sweep 1440/390; Hallmark + Vercel audits → `docs/audits/`.

## Phase 10 — Automation suite
- `pytest.ini`: `DJANGO_SETTINGS_MODULE=config.settings`, markers `admin customer ai e2e unit negative tc(id)`, `addopts = --html=reports/report.html --self-contained-html -p no:randomly`(random order only in rule check run).
- `tests/conftest.py`: sets `DJANGO_ALLOW_ASYNC_UNSAFE=true`; fixtures `admin_user`, `customer` (factory), `catalog_data` (2 categories, 6 products), `logged_in_customer_page`, `admin_page`; screenshot hook → `reports/screenshots/<test>.png` + pytest-html image extra; results recorder writes `reports/last_run.json`, then runs `python manage.py record_test_run reports/last_run.json` in a subprocess at session end (so it writes to the real reports DB, never the test DB).
- `tests/catalog.py`: `TEST_CASES: dict[str, dict]` (id → test_name, module, test_description, expected_result); `sync_test_catalog` loads it into `TestCase`.
- Page objects in `tests/pages/`: `LoginPage`, `AdminLoginPage`, `ProductPage`, `CartPage`, `CheckoutPage`, `PaymentPage`, `AdminProductsPage`, …
- Tests: 22 admin, 27 customer, 8 negative extras, 8 AI, 4 E2E (names per BUILD_PROMPT 10.3–10.7), each tagged `@pytest.mark.tc("…")`.
- `run_tests.ps1 [-Suite all|admin|customer|ai|e2e|unit] [-Headed] [-SlowMo 400]`.

## Phase 11–12
Docs (diagrams, README, CODE_MAP, TEST_CASES, matrix), fresh-clone + offline check, security check, `reset_demo`, push.
