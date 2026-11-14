# BUILD_PROMPT.md — Step-by-step build plan

> **For Krishna (how to start):**
> 1. Create the folder `D:\Internship Projects\ai-multicategory-ecommerce` and put `CLAUDE.md`, `BUILD_PROMPT.md`, `PROGRESS.md` and `docs/PROJECT_BRIEF.md` in it.
> 2. Create an empty public GitHub repo named `ai-multicategory-ecommerce` (no README).
> 3. Open the folder in VS Code → Claude Code → set effort to **High**.
> 4. Paste this as the first message:
>    `Read CLAUDE.md, PROGRESS.md and BUILD_PROMPT.md fully. Then start BUILD_PROMPT.md from the first unchecked step and keep going phase by phase. Follow every step; do not skip anything. Update PROGRESS.md after every step.`
> 5. In every new session after that, paste:
>    `Read CLAUDE.md and PROGRESS.md, then continue BUILD_PROMPT.md from the first unchecked step.`

---

**Instructions to Claude Code:** Work through the phases in order. Each step has a checkbox; tick it in THIS file and log it in `PROGRESS.md` only after it is verified (server run, page checked, tests passed). Each phase ends with a **Gate** — do not start the next phase until the gate passes. Commit at the end of every phase.

---

## Phase 0 — Setup & research
- [x] 0.1 Confirm the toolkit is available: `/plugin` (Superpowers, Last30days, Diagram Design), `claude mcp list` (Playwright, Context7), `npx skills ls -g` (Hallmark, GSAP skills, Vercel web-design-guidelines, Humanizer). Note anything missing in PROGRESS.md and continue.
- [x] 0.2 Read `docs/PROJECT_BRIEF.md` completely. Create `docs/REQUIREMENTS_MATRIX.md`: one row for EVERY brief item (each admin feature, customer feature, AI functionality, AI output field, implementation rule bullet, test case, E2E scenario, report item) with columns: `ID | Brief item | Implemented in | Covered by test | Status`.
- [x] 0.3 **Last30days** research: current e-commerce storefront UI/UX trends (homepage layouts, product cards, quick-view, sponsored/deal sections, mega menus, cart & checkout UX, micro-interactions, mobile patterns). Save a short summary with the 8–12 most useful patterns to `docs/research/ui-trends.md`.
- [x] 0.4 **Context7**: pull current docs for Django (auth, forms, transactions, `select_for_update`, file email backend, management commands), pytest-django (`live_server`, db access), Playwright-Python (sync API, locators, `expect`, tracing/screenshots), pytest-html, scikit-learn (`TfidfVectorizer`, `cosine_similarity`), Bootstrap 5, GSAP + ScrollTrigger, Lenis. Note the versions to pin.
- [x] 0.5 Python venv + pinned `requirements.txt` (Django, scikit-learn, pandas, numpy, Pillow, python-dotenv or django-environ, pytest, pytest-django, pytest-playwright, pytest-html, playwright). Install. `python -m playwright install chromium`.
- [x] 0.6 `git init`, `.gitignore`, `.env.example`, add remote `origin` (github.com/Krishna141414/ai-multicategory-ecommerce), first commit.
- **Gate 0:** venv works, `python -m django --version` and `pytest --version` run, matrix file exists with all brief items.

## Phase 1 — Plan & design direction
- [x] 1.1 `/superpowers:brainstorming` on the whole system (use the brief + CLAUDE.md as input). Then `/superpowers:writing-plans` → save the implementation plan to `docs/plans/implementation-plan.md` (apps, models, services, URLs, templates, JS, tests). (If the command names differ, use the Superpowers skills listed in the `/` picker.)
- [x] 1.2 **Hallmark study + direction**: using `docs/research/ui-trends.md`, decide the store name, brand personality, colour palette (with CSS variables and contrast-checked values), typography (self-hosted fonts), spacing scale, radius, shadows, icon set, motion principles (where motion is used and where not). Write it to `docs/DESIGN_SYSTEM.md` and the reasons to `docs/DECISIONS.md`. Must satisfy the guardrails in CLAUDE.md §2 (industry-grade, not template-like, not AI-looking).
- [x] 1.3 Page inventory with a one-line purpose each (customer: home, category, search/results, product detail, cart, checkout, payment, confirmation, orders, order detail, profile, queries, conversation, AI explainer, login, register; admin: login, dashboard, categories, products, customers, orders, ratings/reviews, queries, conversation, test reports). Save to `docs/plans/pages.md`.
- **Gate 1:** plan, design system and page inventory written and committed.

## Phase 2 — Project scaffold, models, seed data
- [x] 2.1 Django project + apps (suggested split: `accounts`, `catalog`, `orders` (cart/checkout/payment), `reviews`, `messaging`, `recommender`, `adminpanel`, `testreports` — adjust if the plan says otherwise). Settings read `.env`. Static + media configured. File-based email backend → `sent_emails/`.
- [x] 2.2 Models with **all brief fields** + DB constraints: Customer profile, Category, Product (+ `is_sponsored`), Cart item, Order (one row per item, shared `order_id`, `product_name` snapshot, `amount`), Payment, Rating, Review, Message, ProductFeature, CustomerProductInteraction, TestCase, TestExecution, TestSummary (report models live in a separate reports store/DB per CLAUDE.md). Migrations run clean.
- [x] 2.3 Vendor assets downloaded locally into `static/vendor/`: Bootstrap 5 (CSS+JS bundle), GSAP + ScrollTrigger, Lenis, chosen icon set, self-hosted fonts. No CDN references anywhere.
- [x] 2.4 Seed data (management command `seed_demo`, idempotent): the 10 brief categories with descriptions; ≈10–12 products per category (≈100–120) with **fictional brands**, realistic names, prices in ₹, stock (include a few out-of-stock), rich descriptions + keywords good enough for TF-IDF to find real similarity; mark ~8 as sponsored. Use **Humanizer** so descriptions read naturally.
- [x] 2.5 Product images: real photos with a free licence (prefer Openverse / Wikimedia Commons CC0/CC-BY, or Pexels/Unsplash), downloaded once into `media/products/`, credits listed in `docs/IMAGE_CREDITS.md`. If a suitable image can't be found, use a clean designed placeholder consistent with the design system. Images must match the product type.
- [x] 2.6 Management commands: `create_default_admin` (from `.env`), `seed_demo` (categories, products, 3–4 demo customers, some past orders, ratings, reviews, a couple of conversations, interactions), `reset_demo` (wipe + reseed for a clean video run).
- **Gate 2:** `migrate` + `create_default_admin` + `seed_demo` run cleanly; Django shell shows correct counts; commit.

## Phase 3 — Authentication & roles
- [x] 3.1 Customer registration (all brief fields, unique email, password hashed, Active by default), customer login (email + password), logout.
- [x] 3.2 Admin login (username + password), logout. Invalid logins show a clear error (no detail leaks).
- [x] 3.3 Deactivated customer cannot log in (clear message). Role decorators/mixins: customer-only pages and admin-only pages; wrong role → redirect/403.
- [x] 3.4 View/update profile (server-side validation; email stays unique).
- **Gate 3:** manually verify every auth path in the browser via Playwright MCP; commit.

## Phase 4 — Admin panel (custom UI, not Django's /admin)
- [x] 4.1 Dashboard: total_customers, total_categories, total_products, total_orders, total_sales (+ small recent-orders table and a simple sales/orders chart if it fits the design).
- [x] 4.2 Categories: add, view (list with search), update, delete (block or confirm when products exist — decide and document).
- [x] 4.3 Products: add (image upload, validation price > 0, qty ≥ 0, sponsored toggle), view (list with filters), update, delete (soft delete when it has orders).
- [x] 4.4 Customers: view list/detail, activate / deactivate.
- [x] 4.5 Orders: view (grouped by `order_id`, expandable items), update status (Pending/Confirmed/Shipped/Delivered/Cancelled; cancelling restores stock).
- [x] 4.6 Ratings & reviews: view all with product + customer + date.
- [x] 4.7 Queries: view inbox, post a query to a customer, reply, view full conversation history (threaded).
- **Gate 4:** every admin feature works end-to-end in the browser (Playwright MCP screenshots); matrix updated; commit.

## Phase 5 — Customer catalogue
- [x] 5.1 View categories (category grid/menu).
- [x] 5.2 View products (listing with pagination/sorting) and **search** by product_name, category, min_price, max_price (combinable; validated; empty-result state).
- [x] 5.3 Product details: product_name, category, brand, price, description, image, available_quantity, average rating, reviews list; out-of-stock state; log a `view` interaction.
- **Gate 5:** search combinations verified; commit.

## Phase 6 — Cart, checkout, dummy payment, orders, email
- [x] 6.1 Add to cart (login required; blocks zero stock and qty > stock; logs `cart` interaction), view cart, update quantity, remove item, live totals.
- [x] 6.2 Submit cart → service function in one `transaction.atomic()` with `select_for_update` stock check + reservation → one order row per item, shared `order_id`, `amount = price × qty`, status Pending, total computed. Duplicate-submit guard.
- [x] 6.3 Dummy payment page: choose method, simulate Success/Failure. Success → orders Confirmed, Payment row, cart cleared, `purchase` interactions logged, order email written to `sent_emails/`, confirmation page. Failure → nothing confirmed, retry possible. Idempotent on repeat.
- [x] 6.4 Order confirmation page, order history (grouped by `order_id`, with status badges), order details.
- [x] 6.5 Unit tests (plain pytest, no browser) for the checkout + payment service: totals, stock reservation, rollback on failure, no duplicate orders, cancel restores stock.
- **Gate 6:** full shopping flow verified in the browser + service tests pass; commit.

## Phase 7 — Ratings, reviews, queries (customer side)
- [x] 7.1 Add rating (1–5) and add review (only for purchased products; one rating per product, editable).
- [x] 7.2 Post query (new conversation), view own queries, reply, view conversation history. Customers can only see their own conversations (test this with a second customer).
- **Gate 7:** verified with two customers + admin replying; commit.

## Phase 8 — AI recommender + AI Explainer
- [x] 8.1 `recommender/` module: collect product info → Pandas preprocessing → TF-IDF features → cosine similarity → cached matrix, rebuilt when products change (signal or explicit rebuild + management command `build_recommender`). Keep `ProductFeature` in sync.
- [x] 8.2 Similar products on product page (exclude self; active + in-stock only; show name, category, image, price, similarity score).
- [x] 8.3 Personalised "Recommended for you" (home + a dedicated "View AI Recommended Products" page): interests from viewed/cart/purchased with weights, exclusions, top-N with scores and a "because you viewed …" reason. New-customer fallback: popular / category-based.
- [x] 8.4 **AI Explainer page**: choose any product → animated steps with Next/Back (and optional autoplay with pause): (1) raw product text, (2) cleaned/combined text, (3) top TF-IDF terms with weight bars, (4) similarity scores against other products (sorted), (5) final top-N cards. Plus a small panel explaining personalised recs for the logged-in customer (their interests → aggregated scores).
- [x] 8.5 Plain pytest unit tests for the engine: feature extraction shape/terms, self-exclusion, inactive/out-of-stock exclusion, relevance (top results share category/keywords), new-customer fallback.
- **Gate 8:** recommendations look sensible for at least 5 sample products across categories (write examples into `docs/research/recommender-check.md`); commit.

## Phase 9 — UI design pass & polish
- [x] 9.1 Apply the design system everywhere (base template, header with category/mega menu, search, cart badge, footer, mobile bottom nav if chosen).
- [x] 9.2 **Homepage**: hero + **Sponsored / Featured deals** (animated carousel/strip, pauses on hover, **hover quick-view card** with image, price, rating, stock, add-to-cart; keyboard accessible; works on touch with tap) + categories + recommended-for-you + best sellers / new arrivals, laid out per the design direction.
- [x] 9.3 Micro-interactions: add-to-cart feedback (button state + cart badge bump), toasts, skeletons where content loads, hover states, subtle scroll reveals (GSAP/ScrollTrigger, `gsap-performance` rules, `prefers-reduced-motion` respected). Smooth scroll with Lenis only if it doesn't fight the UI.
- [x] 9.4 Admin UI: clean dashboard look consistent with the brand, readable tables, status badges, confirmation dialogs.
- [x] 9.5 **Playwright MCP sweep**: screenshot EVERY page at 1440 px and 390 px, logged-out / customer / admin. Fix overlaps, overflow, broken images, misalignment.
- [x] 9.6 **Hallmark audit** on all pages → fix findings. Then **Vercel Web Design Guidelines** audit → fix findings (focus states, labels, contrast, forms, motion, performance). Save both audit summaries to `docs/audits/`.
- **Gate 9:** no page looks like a stock Bootstrap template; screenshots saved to `screenshots/`; commit.

## Phase 10 — Playwright + Pytest automation suite
- [x] 10.1 Structure: `tests/` with `conftest.py` (live_server, browser/page fixtures, controlled test data factories, screenshot-on-failure hook, results recorder), `tests/pages/` (page objects), `tests/admin/`, `tests/customer/`, `tests/ai/`, `tests/e2e/`, `tests/unit/`. `pytest.ini` with markers `admin, customer, ai, e2e, unit, negative` and pytest-html output to `reports/report.html` (self-contained).
- [x] 10.2 Test case catalogue (one source, e.g. `tests/test_catalog.py` or YAML) with `id, test_name, module, test_description, expected_result`; every test linked to its ID (marker or decorator). Catalogue synced into the TestCase table.
- [x] 10.3 **Admin tests (22):** TC-ADM-01 Admin Login · 02 Invalid Admin Login · 03 View Dashboard · 04 Add Category · 05 View Categories · 06 Update Category · 07 Delete Category · 08 Add Product · 09 View Products · 10 Update Product · 11 Delete Product · 12 View Customers · 13 Activate Customer · 14 Deactivate Customer · 15 View Orders · 16 Update Order Status · 17 View Product Ratings/Reviews · 18 View Queries · 19 Post Query · 20 Reply Query · 21 View Conversation History · 22 Logout.
- [x] 10.4 **Customer tests (27):** TC-CUS-01 Registration · 02 Login · 03 Invalid Login · 04 View Profile · 05 Update Profile · 06 View Product Categories · 07 Search by Name · 08 Search by Category · 09 Search by Price · 10 View Products · 11 View Product Details · 12 Add to Cart · 13 View Cart · 14 Update Cart Quantity · 15 Remove from Cart · 16 Submit Cart · 17 Dummy Payment · 18 View Order Confirmation · 19 View Order History · 20 View Order Details · 21 Add Rating · 22 Add Review · 23 Post Query · 24 View Queries · 25 Reply Query · 26 View Conversation History · 27 Logout.
- [x] 10.5 **Extra negative tests** (beyond the list, mark `negative`): duplicate email registration, deactivated customer login blocked, add out-of-stock product, cart qty > stock, payment failure does not confirm order, customer cannot open admin page, customer cannot see another customer's conversation, invalid price (≤ 0) / negative quantity rejected in admin.
- [x] 10.6 **AI tests (8):** TC-AI-01 Product Feature Extraction · 02 Similar Product Recommendations · 03 Customer-Based Recommendations · 04 Recommended Product Display · 05 Recommended Product Details (name, category, image, price, score) · 06 Recommendation After Product View · 07 Recommendation After Adding to Cart · 08 Recommendation for New Customer. Assert relevance (shared category/keywords, scores sorted, self excluded, only active + in-stock).
- [x] 10.7 **E2E scenarios (4):** E2E-01 Customer Shopping (Register → Login → Search → View → Add to Cart → Submit → Dummy Payment → Confirmation → Logout; verify totals + DB rows + email file) · E2E-02 AI Recommendation (Login → View Product → Recommendations → open a recommended product → Add to Cart) · E2E-03 Admin Product Management (Login → Add Category → Add Product → View → Update → Delete → Logout) · E2E-04 Order Management (Customer places order → Admin views → Admin updates status → Customer sees updated status).
- [x] 10.8 Reporting: screenshot on failure → `reports/screenshots/`; pytest-html report; results recorder writes TestExecution rows (per test) and a TestSummary row (per run) into the reports store; Admin **Test Reports** page lists runs, filters Passed / Failed / Skipped, shows timings, screenshots and links the HTML report.
- [x] 10.9 Rules check: no `time.sleep`, only role/label/text/testid locators, each test runs alone (`pytest -k <name>`) and the whole suite runs in random order cleanly, real `db.sqlite3` unchanged after a run (verify by checksum/row counts).
- [x] 10.10 Convenience scripts (PowerShell): `run_tests.ps1` with options for all / admin / customer / ai / e2e, headless (default) or `-Headed` with slow-mo for the video.
- **Gate 10:** full suite passes headless AND headed; report + screenshots generated; Test Reports page shows the run; commit.

## Phase 11 — Documentation (for GitHub + the video)
- [x] 11.1 **Diagram Design**: architecture diagram (browser → Django apps → services → SQLite; recommender pipeline; test harness → live server → reports). Recommender data-flow diagram. Checkout transaction sequence diagram. Save in `docs/diagrams/`.
- [x] 11.2 `README.md` (Humanizer pass): what it is, features (admin / customer / AI / testing), screenshots preview, tech stack, architecture diagram, setup on Windows step by step (venv, install, `.env`, migrate, `create_default_admin`, `seed_demo`, `build_recommender`, runserver), default admin credentials note (change before deployment), how to run tests (headed/headless, by marker), where reports/screenshots go, project structure, limitations.
- [x] 11.3 `docs/CODE_MAP.md`: every file/folder → its job; main functions/classes per file; how files connect in order for each flow (register/login, browse/search, cart → checkout → payment → email, recommendation, queries, admin management, test run → reports). Written so the owner can explain it on video.
- [x] 11.4 `docs/TEST_CASES.md`: the full catalogue table (id, name, module, description, expected result) + latest run summary.
- [x] 11.5 Finish `docs/REQUIREMENTS_MATRIX.md` — every row Implemented + Tested, or clearly explained.
- **Gate 11:** docs complete and accurate; commit.

## Phase 12 — Final verification & ship
- [x] 12.1 Fresh-clone check: clone into a temp folder, follow README exactly from zero (new venv), confirm the app and the test suite work. Then confirm it runs **with the internet off** (no CDN/network calls).
- [x] 12.2 `/superpowers:verification-before-completion` (or the equivalent skill) across the whole matrix.
- [x] 12.3 Final Playwright MCP screenshot sweep → save the best ones to `screenshots/` (home, sponsored hover quick-view, product + similar products, recommendations, AI explainer, cart, payment, confirmation, admin dashboard, admin orders, test reports page, pytest-html report).
- [x] 12.4 Security check: no secrets committed, `.env.example` complete, CSRF on all forms, role checks on every view, DEBUG from env.
- [x] 12.5 `reset_demo` so the database is clean for recording; final commit; push to GitHub.
- **Gate 12:** pushed; README renders correctly on GitHub; PROGRESS.md says DONE with a short summary of what was built and how to run the demo.
