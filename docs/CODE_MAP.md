# Code map

A tour of the Velora code, written to be explained out loud. Part 1 shows how one request travels through the code. Part 2 goes folder by folder: what each file is for and its main functions and classes. Part 3 follows each feature from click to database, naming the file and function at every step. Part 4 suggests an order for a video walkthrough.

Diagrams that go with this page: [architecture](diagrams/architecture.html), [recommender data flow](diagrams/recommender.html), [checkout sequence](diagrams/checkout.html).

---

## Part 1. How a request travels

Every page follows the same path. Take "a customer opens a product page":

1. **`config/urls.py`** matches the URL. It hands `/product/<slug>/` to `catalog/urls.py`, which names the view `catalog.views.product_detail`.
2. **Middleware** runs first. Django's own middleware handles sessions, CSRF and login; ours, `core/middleware.py` `ActiveCustomerMiddleware`, signs out a customer whose account was deactivated while they were signed in.
3. **The view** (`catalog/views.py` `product_detail`) checks permissions where needed (`core/permissions.py`), then asks **service modules** for the data. Views stay short on purpose: they read the request, call services, and choose a template.
4. **Services** hold the rules (`catalog/services.py`, `orders/services/…`, `reviews/services.py`, `messaging/services.py`, `recommender/engine.py`). They use the **models** to read and write the database.
5. **Models** (`*/models.py`) are the database tables. Shop tables live in `db.sqlite3`; test-result tables live in `reports.sqlite3`. `config/db_router.py` decides which file a model uses.
6. **The template** (`templates/catalog/product_detail.html`) builds the HTML. It extends `templates/base.html` (header, footer, toasts, scripts) and receives extra values from `core/context_processors.py` (store name, category menu, cart count) on every page.
7. **Static files** style and animate it: `static/css/tokens.css` (colours, fonts, spacing), `base.css` (shared components), `store.css` (storefront) or `admin.css` (admin), and `static/js/*.js` for the interactive parts.

Most apps follow this layout: `models.py` (tables), `services.py` (rules), `forms.py` (input validation), `views.py` (pages), `urls.py` (addresses), and templates in `templates/<app>/`.

---

## Part 2. Folder by folder

### `config/`: project settings and wiring

| File | What it does | Main parts |
|---|---|---|
| `settings.py` | All Django settings. Reads secrets from `.env` with python-dotenv. Two databases, the email backend (files in `sent_emails/` or SMTP), recommender settings, `REPORTS_DIR`. | `env_bool`, `env_list`; `DATABASES` (`default` = shop with SQLite IMMEDIATE transactions, `reports` = test results); `RECOMMENDER` (top-N, interaction weights, half-life); `STORE_NAME`, `ASSET_VERSION` |
| `urls.py` | The URL map. Customer pages at the root, the admin panel under `/manage/`, queries under `/queries/`, product photos under `/media/`. | `urlpatterns` |
| `db_router.py` | Sends the `testreports` models to `reports.sqlite3` and everything else to `db.sqlite3`, so a test run can never touch shop data. | `ReportsRouter` (`db_for_read`, `db_for_write`, `allow_migrate`) |
| `asgi.py`, `wsgi.py` | Standard Django entry points for a web server. | |

### `core/`: things every page needs

| File | What it does | Main parts |
|---|---|---|
| `views.py` | The home page: hero deal, sponsored strip, aisles, recommended, best sellers, new arrivals. | `home`, `hero_offer` |
| `permissions.py` | Who may open what. Used as decorators on every view. | `get_customer`, `customer_required` (signed-in active customer, sets `request.customer`), `admin_required` (staff only) |
| `middleware.py` | Signs out a customer who was deactivated mid-session. | `ActiveCustomerMiddleware` |
| `context_processors.py` | Values every template gets: store name, asset version, category bar, lazy mega menu, current customer, cart count. | `store_context` |
| `templatetags/shop_tags.py` | Template filters. | `inr` (₹ with Indian digit grouping, `1,24,999.50`), `add_class`, `star_list`, `get_item` |
| `demo.py` | Builds the demo store. | `seed_catalog`, `seed_customers`, `seed_orders`, `seed_carts_and_views`, `seed_conversations` |
| `management/commands/seed_demo.py` | `python manage.py seed_demo`: loads the demo data (safe to run twice). | `Command` |
| `management/commands/reset_demo.py` | `python manage.py reset_demo --yes`: wipes shop data and reloads the demo. Test reports are kept. | `Command` |

### `accounts/`: customers and sign-in

| File | What it does | Main parts |
|---|---|---|
| `models.py` | The customer profile with the brief's fields, linked one-to-one to Django's `User` (which stores the hashed password). | `Customer` (name, email (unique, case-insensitive), mobile_number, address, registered_date, status) |
| `backends.py` | Lets customers sign in with **email** + password. | `EmailBackend.authenticate` |
| `forms.py` | Registration, customer login, admin login and profile forms. All checks run on the server. | `RegistrationForm` (`clean_mobile` accepts `+91 98765 43210` and stores 10 digits), `CustomerLoginForm`, `AdminLoginForm`, `ProfileForm` |
| `services.py` | Account rules shared by views and commands. | `register_customer` (User + Customer, Active), `login_error_for` (says "deactivated" when that is the reason), `set_customer_status` (keeps `User.is_active` in step), `ensure_default_admin`, `default_admin` |
| `views.py` | Register, login, logout (POST only), profile, edit profile. | `register`, `login_view`, `logout_view`, `profile`, `profile_edit` |
| `management/commands/create_default_admin.py` | `python manage.py create_default_admin [--reset-password]`: creates the admin from `.env`. | `Command` |

### `catalog/`: categories and products

| File | What it does | Main parts |
|---|---|---|
| `models.py` | Categories and products with database rules: price > 0, quantity ≥ 0, MRP ≥ price. | `Category`, `Product` (+ `is_sponsored`, `slug`, `mrp`), `ProductQuerySet.active()` and `.available()` (active and in stock), properties `in_stock`, `discount_percent`, `image_url`, `keyword_list` |
| `services.py` | Catalogue rules for both the admin and the storefront. | `search_products` (name, category, min/max price, in stock, sort; all combinable), `delete_product` (hard delete, or hide it if it has orders so history stays intact), `delete_category` (refused while it has products), `with_ratings`, `storefront_categories`, `category_cover`, `product_reviews`, `rating_breakdown`, `mega_menu` |
| `forms.py` | The storefront search form. | `ProductSearchForm` (validates min ≤ max), `active_filters` |
| `views.py` | Category grid, product list and search, product page, quick-view fragment. | `category_list`, `product_list`, `product_detail` (logs a view, loads similar products and the buyer's own rating/review), `quick_view` |
| `seed_data.py` | The 10 categories, 110 products with fictional brands, and the 4 demo customers. | `CATEGORIES`, `PRODUCTS`, `DEMO_CUSTOMERS` |

### `orders/`: cart, checkout, payment, orders

| File | What it does | Main parts |
|---|---|---|
| `models.py` | Cart lines, order rows and payments. | `CartItem`; `Order` (one row per product, rows of one checkout share `order_id`, `amount = price × quantity` set in `save()`, `product_name`/`price` copied so history never breaks); `OrderStatus` (Pending, Confirmed, Shipped, Delivered, Cancelled); `Payment` (one success per order, enforced by a unique constraint) |
| `services/cart.py` | Cart rules: several products, quantity never above stock. | `get_cart` (`CartSummary` with lines, total and stock problems), `add_to_cart` (also logs a `cart` interaction), `update_quantity`, `remove_item`, `CartError` |
| `services/checkout.py` | **Submit Cart** in one database transaction. | `submit_cart` (re-checks stock, reserves it with a conditional decrement, creates the order rows, returns `order_id`; the same `checkout_key` returns the same order, so a double click can't create two), `new_order_id` (`ORD-20261109-7K3Q`), `order_total`, `is_paid`, `_release_unpaid_orders` |
| `services/payment.py` | The dummy payment. | `pay` (records a `Payment`; on success: orders Confirmed, cart cleared, `purchase` interactions logged, email sent after commit; on failure: order stays Pending; paying twice never charges twice) |
| `services/status.py` | Admin status changes. | `next_statuses` (allowed moves), `set_order_status` (cancelling puts the stock back) |
| `services/queries.py` | Read-only order helpers for the admin and the history page. | `order_groups` (one entry per `order_id`), `total_sales`, `status_counts`, `paid_order_ids` |
| `emails.py` | The order confirmation email (text + HTML). | `send_order_email` |
| `forms.py` | The payment form: method + "Payment succeeds / fails". | `PaymentForm` |
| `views.py` | Cart, checkout, payment, confirmation, history, detail. Cart endpoints answer JSON for the page's JavaScript and redirect otherwise. | `cart`, `cart_add`, `cart_update`, `cart_remove`, `checkout`, `payment`, `confirmation`, `history`, `detail`, `status_track` |

### `reviews/`: ratings and reviews

| File | What it does | Main parts |
|---|---|---|
| `models.py` | Two separate tables, as in the brief. One per customer per product. | `Rating` (1 to 5), `Review` |
| `services.py` | Only buyers (Confirmed, Shipped or Delivered order) may rate or review; saving again updates. | `can_review`, `save_rating`, `save_review`, `my_feedback`, `ReviewError` |
| `forms.py` | Star rating form and review form. | `RatingForm`, `ReviewForm` |
| `views.py` | Both forms post here from the product page and return to it. | `rate`, `review` |

### `messaging/`: customer questions and replies

| File | What it does | Main parts |
|---|---|---|
| `models.py` | **One** messages table for queries and replies (brief rule 6). | `Message` (conversation_id, sender/receiver + their types, parent_message, subject, message, posted_date, status Unread/Read), `Role` |
| `services.py` | Conversation rules. | `start_conversation` (new `conversation_id`, `parent_message = NULL`), `start_customer_query` (goes to the store admin), `reply` (same `conversation_id`, parent = the latest message), `thread` + `ensure_can_view` (a customer only sees their own conversations), `mark_read`, `conversations_for` |
| `forms.py` | Query and reply forms. | `QueryForm`, `AdminQueryForm` (choose a customer), `ReplyForm` |
| `views.py` | Customer side: list, new query, conversation with reply. | `query_list`, `query_new`, `query_thread` |

### `recommender/`: the AI

| File | What it does | Main parts |
|---|---|---|
| `models.py` | The brief's two AI tables. | `ProductFeature` (category, product_name, brand, description, keywords, price per product), `CustomerProductInteraction` (view / cart / purchase with a date) |
| `features.py` | Keeps `ProductFeature` in step with the catalogue. | `sync_feature`, `sync_all_features`, signal handlers on Product and Category save |
| `interactions.py` | Records what customers do. | `log_interaction` (repeat views within 10 minutes count once) |
| `engine.py` | **The recommender.** Pipeline: collect → clean → combine → TF-IDF → cosine similarity → recommend. | `build_frame` (Pandas DataFrame), `clean_text`, `weighted_document` (name and keywords ×3, category ×2), `Engine` (`similar`, `interests`, `personalized`, `top_terms`, `shared_terms`, `explain`), `popular` (new customers), `Recommendation`, `get_engine` (cached until products change) |
| `views.py` | "Recommended for you" and the AI Explainer. | `recommended`, `explainer`, `explainer_data` (JSON) |
| `management/commands/build_recommender.py` | `python manage.py build_recommender`: syncs features and rebuilds the matrix now. | `Command` |

### `adminpanel/`: the admin panel (`/manage/`)

| File | What it does | Main parts |
|---|---|---|
| `views/auth.py` | Admin login (username + password, staff only) and logout. | `admin_login`, `admin_logout` |
| `views/dashboard.py` + `services.py` | The five totals, orders by status, recent orders, a 14-day chart. | `dashboard`; `dashboard_stats`, `daily_series`, `recent_orders` |
| `views/categories.py`, `views/products.py` | Add, view, edit and delete; the sponsored toggle. | `category_*`, `product_*`, `product_toggle_sponsored` |
| `views/customers.py` | Customer list and detail, activate/deactivate. | `customer_list`, `customer_detail`, `customer_set_status` |
| `views/orders.py` | Orders grouped by `order_id`, status updates. | `order_list`, `order_detail`, `order_update_status` |
| `views/reviews.py` | Ratings and reviews. | `review_list` |
| `views/queries.py` | Inbox, new query to a customer, conversation with reply. | `query_inbox`, `query_new`, `query_thread` |
| `views/reports.py` | **Test Reports**: runs, filters, screenshots, HTML reports. | `report_list`, `report_detail`, `report_file` (serves files from `reports/`, never outside it) |
| `views/common.py` | Shared helpers. | `paginate`, `query_without_page`, `safe_next` |
| `forms.py` | Admin forms with the brief's rules. | `CategoryForm`, `ProductForm` (price > 0, quantity ≥ 0, image checks), `OrderStatusForm` (only allowed next statuses) |

### `testreports/`: stored test results (`reports.sqlite3`)

| File | What it does | Main parts |
|---|---|---|
| `models.py` | The brief's three report tables. | `TestCase` (id, test_name, module, test_description, expected_result), `TestSummary` (one per run), `TestExecution` (one per test per run, with screenshot path) |
| `services.py` | Turns a run's `results.json` into rows. | `sync_catalog`, `record_run` |
| `management/commands/record_test_run.py` | Called automatically after each pytest run. | `Command` |
| `management/commands/sync_test_catalog.py` | Copies `tests/catalog.py` into `TestCase`. | `Command` |
| `management/commands/clean_test_reports.py` | Lists report folders as linked or leftover; `--delete` removes only leftovers. | `Command`, `linked_run_names` |

### `templates/`: the HTML

- `base.html`: every storefront page's frame (head, header, toasts, footer, phone tab bar, scripts). `403.html`, `404.html`: error pages.
- `partials/`: `header.html` (search, account menu, cart badge, mega menu, category rail), `footer.html`, `tab_bar.html` (phones), `toasts.html`, `field.html` (one form field with its error), `stars.html`, `thread.html` (a conversation).
- `core/home.html`; `catalog/` (`categories`, `product_list`, `product_detail`, `_product_card`, `_quick_view`); `orders/` (`cart`, `checkout`, `payment`, `confirmation`, `history`, `detail`, `_steps`); `reviews/_feedback.html`; `messaging/` (`list`, `new`, `thread`); `recommender/` (`recommended`, `explainer`, `_rec_card`, `_similar`); `accounts/` (`register`, `login`, `profile`, `profile_edit`, `_account_nav`, `_auth_aside`).
- `adminpanel/`: its own `base.html` (sidebar + top bar), `login.html`, `dashboard.html`, and a folder per area including `reports/`.
- `emails/order_confirmation.txt` and `.html`: the order email.

### `static/`: CSS, JavaScript, fonts, libraries

| File | What it does |
|---|---|
| `css/tokens.css` | The design system's values: colours (OKLCH), fonts, type scale, spacing, motion timings |
| `css/base.css` | Shared pieces on top of Bootstrap: buttons, forms, badges, toasts, skeletons, tables, focus rings, reduced motion |
| `css/store.css` | Storefront: header and mega menu, cards, product page, cart and checkout, home, quick view, Explainer |
| `css/admin.css` | Admin panel layout, tables, dashboard, reports |
| `js/app.js` | Site-wide behaviour, as `window.Chowk` (the store's working name, kept in code): toasts, cart badge, submit-button spinners, confirm dialogs, quantity steppers, add to cart without reloading, live cart totals |
| `js/quickview.js` | One quick-view panel for the whole store (hover, click, tap; Esc closes) |
| `js/sponsored.js` | The drifting sponsored strip (GSAP), pause rules, prev/next |
| `js/explainer.js` | The AI Explainer's step-by-step controls and bar animations |
| `js/motion.js` | Subtle scroll reveals (GSAP ScrollTrigger), off under reduced motion |
| `vendor/`, `fonts/` | Bootstrap, Bootstrap Icons, GSAP and the two font families, stored locally (no CDN) |

### `tests/`: the automated tests

| File | What it does |
|---|---|
| `conftest.py` | Shared setup: the `site` fixture (live test server), `as_customer` / `as_admin` (sign in by session cookie), screenshot on failure, results recorder that calls `record_test_run` at the end |
| `catalog.py` | The 69 test cases (id, name, module, description, expected result) |
| `factories.py` | Test data: `make_shop` (two aisles), `make_customer`, `make_admin`, `make_order` |
| `pages/__init__.py` | Page objects: `CustomerLoginPage`, `RegisterPage`, `AdminLoginPage`, `ProductPage`, `CartPage`, `CheckoutPage`, `PaymentPage` |
| `admin/test_admin.py` | TC-ADM-01 to 22 |
| `customer/test_account.py`, `test_shopping.py`, `test_feedback_queries.py` | TC-CUS-01 to 27 |
| `customer/test_negative.py` | TC-NEG-01 to 08 |
| `ai/test_ai.py` | TC-AI-01 to 08 |
| `e2e/test_workflows.py` | E2E-01 to 04 |
| `unit/` | 117 fast tests of the rules (models, auth, search, checkout, payment, reviews, queries, engine, reports, catalogue coverage) |

### Other files

| File | What it does |
|---|---|
| `manage.py` | Django's command-line entry point |
| `run_tests.ps1` | Runs the tests (suites, headed, slow motion, random order) |
| `requirements.txt` | Pinned Python packages |
| `.env.example` | The settings to copy into `.env` |
| `scripts/import_manual_photos.py`, `scripts/brand_labels.py` | One-off tools used to prepare product photos (crop, fictional brand labels) |
| `scripts/build_diagrams.py` | Rebuilds the diagrams in `docs/diagrams/` |
| `media/products/` | Product photos (credits in `docs/IMAGE_CREDITS.md`) |

---

## Part 3. Each flow, step by step

### Register and sign in

1. `accounts/views.py` `register` shows `RegistrationForm` (`accounts/forms.py`).
2. On submit the form validates on the server: required fields, email not taken (any case), mobile normalised to 10 digits, password rules, passwords match.
3. `accounts/services.py` `register_customer` creates the `User` (password hashed by Django) and the `Customer` with status Active, in one transaction.
4. The view signs the customer in and shows a welcome toast.
5. Later sign-ins: `login_view` → `CustomerLoginForm` → `accounts/backends.py` `EmailBackend.authenticate` finds the user by email. A deactivated customer gets the message from `login_error_for` ("…deactivated…") instead of a generic error.
6. On every later request `core/middleware.py` `ActiveCustomerMiddleware` signs out anyone who has since been deactivated, and `core/permissions.py` `customer_required` guards customer pages.
7. Admins sign in at `/manage/login/` through `adminpanel/views/auth.py` `admin_login` with a username; customer accounts can't sign in there, and customers get 403 on admin URLs.

### Browse and search

1. `catalog/views.py` `category_list` → `catalog/services.py` `storefront_categories` (counts) + `category_cover` (a photo per aisle).
2. `product_list` (also used for `/category/<slug>/`) builds `ProductSearchForm` from the query string, then `search_products` filters by name, category, price range and stock, and sorts. Results are paginated; filters stay in the URL.
3. The template renders each result with `templates/catalog/_product_card.html`.
4. The header search box and the mega menu (`mega_menu`, made lazily in `core/context_processors.py`) lead to the same view.

### Product page, similar products and quick view

1. `catalog/views.py` `product_detail` loads an active product.
2. `recommender/interactions.py` `log_interaction(…, VIEW)` records the visit (once per 10 minutes).
3. `recommender/engine.py` `get_engine().similar(product.id)` returns the top 6 similar products (never itself, only active and in stock), shown by `templates/recommender/_similar.html` and `_rec_card.html` with score and reason.
4. `reviews/services.py` `my_feedback` decides whether the signed-in customer sees the rating and review forms (`templates/reviews/_feedback.html`).
5. Quick view anywhere: `static/js/quickview.js` fetches `/product/<id>/quick-view/` → `catalog/views.py` `quick_view` → `templates/catalog/_quick_view.html`, and binds its Add to cart form through `Chowk.bindAddToCart` (`static/js/app.js`).

### Cart → checkout → payment → email

1. **Add to cart.** The form posts to `orders/views.py` `cart_add`. `static/js/app.js` sends it with `fetch` and asks for JSON. `orders/services/cart.py` `add_to_cart` refuses zero stock or a quantity above stock (`CartError`), adds to an existing line, and logs a `cart` interaction. The view answers `{ok, message, count}`; the page updates the badge and shows a toast.
2. **Cart.** `cart` → `get_cart` returns lines at live prices, the total and any stock problems. Changing a quantity calls `cart_update` → `update_quantity`; the page updates the line and total without reloading. `cart_remove` → `remove_item` after a confirm dialog.
3. **Review the order.** `checkout` (GET) checks the cart again, puts a fresh `checkout_key` in the session and shows the items, address and total.
4. **Place the order.** `checkout` (POST) checks the key, then `orders/services/checkout.py` `submit_cart` runs **one transaction**: cancel this customer's older unpaid checkouts (stock goes back), lock and re-check stock, decrement it with a conditional update (`quantity >= ordered`), and create one `Order` row per item, all sharing a new `order_id`, each Pending with `amount = price × quantity`. If any item is short, the whole thing rolls back. Re-sending the same key returns the same order.
5. **Pay.** `payment` shows `PaymentForm` (method, plus "succeeds" or "fails"). `orders/services/payment.py` `pay` records a `Payment` row.
   - Success: every row of the order becomes Confirmed, the cart lines are deleted, `purchase` interactions are logged, and `orders/emails.py` `send_order_email` is scheduled with `transaction.on_commit`, so it only goes out if everything saved. The customer lands on `confirmation`.
   - Failure: nothing is confirmed, the cart stays, and the page explains and offers a retry.
   - Paying an already paid order just shows the confirmation (no second charge).
6. **Afterwards.** `history` (grouped with `orders/services/queries.py` `order_groups`) and `detail` (with `status_track`) show the status the admin sets. The email lands in `sent_emails/` by default.

### Admin manages the store

1. **Products.** `adminpanel/views/products.py` `product_create` / `product_edit` use `ProductForm` (price > 0, quantity ≥ 0, image checks). Saving a product fires the signal in `recommender/features.py`, which updates its `ProductFeature` row, so the recommender rebuilds on next use. `product_delete` → `catalog/services.py` `delete_product` hard-deletes a product without orders and hides one with orders. `product_toggle_sponsored` adds it to the home page strip.
2. **Categories.** `adminpanel/views/categories.py`; `delete_category` refuses while products remain.
3. **Customers.** `customer_set_status` → `accounts/services.py` `set_customer_status` (also flips `User.is_active`, so a deactivated customer can't sign in).
4. **Orders.** `order_update_status` → `OrderStatusForm` (only allowed next statuses) → `orders/services/status.py` `set_order_status` updates every row of the order; Cancelled puts the stock back.
5. **Dashboard.** `adminpanel/services.py` `dashboard_stats` counts customers, categories, products, orders and paid, uncancelled sales.

### Recommendations

1. **Building the model** (`recommender/engine.py`, cached by `get_engine`): `build_frame` reads `ProductFeature` into a Pandas DataFrame → `clean_text` lowercases and strips punctuation and plain numbers → `weighted_document` repeats the name and keywords three times and the category twice → `TfidfVectorizer` (words and two-word phrases, English stop words, terms shared by at least two products) → `cosine_similarity` gives a product × product matrix. It rebuilds only when `fingerprint` (feature count + latest update) changes.
2. **Similar products:** `Engine.similar` sorts one row of the matrix and keeps active, in-stock products; `shared_terms` writes the reason ("Similar to X: wireless, bluetooth").
3. **Recommended for you** (`recommender/views.py` `recommended`, and the home shelf): `Engine.interests` weights the customer's interactions (purchase 3, cart 2, view 1, halving every 14 days); `personalized` averages each product's similarity to those interests, skips the interests themselves and anything in the cart, and names the strongest source ("Because you bought X").
4. **New customers:** `popular` ranks by units ordered, then rating, labelled "Popularity".
5. **AI Explainer:** `recommender/views.py` `explainer` → `Engine.explain` returns every intermediate step; `templates/recommender/explainer.html` shows them and `static/js/explainer.js` steps through them.

### Ratings, reviews and questions

1. **Rate or review:** `templates/reviews/_feedback.html` → `reviews/views.py` `rate` / `review` → `reviews/services.py` `save_rating` / `save_review`. Both call `can_review` (a paid order for the product) and use `update_or_create`, so there is one rating and one review per customer per product.
2. **Ask a question:** `messaging/views.py` `query_new` → `messaging/services.py` `start_customer_query` → a `Message` with a new `conversation_id` and no parent, addressed to the admin.
3. **Reply:** `query_thread` (customer) or `adminpanel/views/queries.py` `query_thread` (admin) → `reply` keeps the `conversation_id` and points at the latest message. Opening a thread runs `thread` + `ensure_can_view` (another customer's thread gives 403) and `mark_read`.

### A test run, from command to report page

1. `run_tests.ps1` (or `python -m pytest`) starts pytest with the options from `pytest.ini` (pytest-html report).
2. pytest-django creates **test databases** (`test_db.sqlite3`, `test_reports.sqlite3`) and, for browser tests, a **live server** in a thread. The real `db.sqlite3` is never opened.
3. Each test builds its data with `tests/factories.py`, signs in with `as_customer` / `as_admin` (or through the form, for login tests), and drives Chromium through page objects in `tests/pages/` using roles, labels, text and `data-testid` only.
4. Assertions use Playwright's `expect`, which waits automatically, plus database checks.
5. `tests/conftest.py` `pytest_runtest_makereport` screenshots any failure into `reports/screenshots/<run>/` and embeds it in the HTML report; `pytest_runtest_logreport` collects each test's result, time and test case id.
6. At the end, `pytest_unconfigure` copies the report into `reports/runs/<run>/`, writes `results.json`, and runs `python manage.py record_test_run` in a separate process. `testreports/services.py` `record_run` saves one `TestSummary` and one `TestExecution` per test into `reports.sqlite3`.
7. The admin opens **Test reports** (`adminpanel/views/reports.py`) to see the run, filter Passed / Failed / Skipped, open screenshots and the HTML report.

---

## Part 4. A suggested order for the video

1. **The store in the browser:** home page (sponsored strip, quick view), search, a product page with similar products.
2. **The shape of the code:** Part 1 above and the [architecture diagram](diagrams/architecture.html): urls → view → service → model → template.
3. **One full purchase**, following "Cart → checkout → payment → email" with `orders/services/checkout.py` `submit_cart` and `orders/services/payment.py` `pay` open side by side. Show the `sent_emails/` file.
4. **The AI:** open the AI Explainer for one product, then `recommender/engine.py` from `build_frame` to `personalized`, using the [recommender diagram](diagrams/recommender.html).
5. **The admin:** dashboard, change an order to Shipped, show the customer sees it.
6. **The tests:** `.\run_tests.ps1 -Suite e2e -Headed` so the browser is visible, then the Test Reports page and the HTML report.
7. **Where each brief item lives:** [REQUIREMENTS_MATRIX.md](REQUIREMENTS_MATRIX.md).
