# CLAUDE.md — AI-Driven Multi-Category E-Commerce (VoidMain Real Project)

Read this file fully at the start of EVERY session, then read `PROGRESS.md`, then continue `BUILD_PROMPT.md` from the first unchecked step.

## 1. What this project is
A complete, locally-running e-commerce store (10 product categories) built with **Django**, with:
- an **Admin** side and a **Customer** side (every feature listed in `docs/PROJECT_BRIEF.md`),
- a local **AI product recommender** (TF-IDF + Cosine Similarity, scikit-learn + Pandas),
- a full **Playwright + Pytest** browser-automation test suite with **pytest-html** reports and failure screenshots.

`docs/PROJECT_BRIEF.md` is the **single source of truth for WHAT to build**. Every line in it must be implemented and traceable. Never drop, rename or "simplify away" a brief feature, field or rule.

The owner (Krishna) will record a **video** explaining the project himself, so the code must be clean, well-organised and easy to explain file by file.

## 2. Who decides what

### Fixed — decided by the owner + brief (do NOT change)
- **Stack:** Python, Django, HTML5, CSS3, JavaScript, **Bootstrap 5**, SQLite, scikit-learn, Pandas, Playwright (Python), Pytest, pytest-html. Django dev server. No React/Next.js, no paid APIs, no LLM.
- **Every feature, field and implementation rule in the brief** (sections Admin, Customer, Categories, AI, Testing, Rules 1–10).
- The **10 categories** exactly as named in the brief.
- **Must-have extras:**
  1. **Sponsored / Featured deals** on the homepage: an animated carousel/strip of sponsored products; **hovering a product shows a quick-view card** (bigger image, price, rating, stock, Add-to-cart). Pauses on hover. Admin marks products as sponsored with a toggle.
  2. **AI Explainer page:** shows step by step how a recommendation is made for a chosen product (cleaned text → top TF-IDF terms with weights → cosine similarity scores → top-N recommendations), animated, with Next/Back controls.
  3. **Admin "Test Reports" page** showing stored test runs (passed / failed / skipped, timings, screenshots, link to the HTML report).
  4. **`docs/CODE_MAP.md`** explaining every file, its main functions/classes, and how files connect — the owner uses it for the video.
- **Guardrails:** must look like a real, industry-grade store — NOT a default Bootstrap template and NOT "AI-generated looking" (no rainbow gradients, no glow-everything, no emoji-heavy UI, no generic purple SaaS look). Good UI with tasteful motion, **not** animation everywhere.
- **Brands must be fictional** (no real brand names/logos such as Flipkart, Amazon, Samsung, Nike, Apple). Product types are real ("wireless earbuds"), brands are invented.
- **Works fully offline** after setup: no CDN links at runtime. Bootstrap, GSAP, Lenis, fonts, icons and product images are stored locally in `static/vendor/` and `media/`.
- Currency: **Indian Rupee (₹)**. Target OS: **Windows + PowerShell**, VS Code.

### Claude Code decides (use the toolkit, then record the decision in `docs/DECISIONS.md`)
- Store name, logo wordmark, **colour palette, typography, spacing, iconography**, layout of every page.
- Which current e-commerce UI patterns to use (research them with Last30days first).
- Where and how animations are used (GSAP / ScrollTrigger / Lenis / CSS), within the "tasteful, not everywhere" guardrail.
- Internal architecture: app split, service layer, URL design, template structure, JS organisation.
- Exact seed products (≈10–12 per category, ≈100–120 total), their descriptions/keywords, and image sourcing.
- Test file layout, page objects, fixtures, markers.
- Any small extra that clearly improves the product **without** breaking a brief rule.

## 3. Toolkit — use these, at the right moment
All are installed globally on the owner's machine. Check with `/plugin`, `claude mcp list`, `npx skills ls -g`. If one is missing, say so and continue with the rest.

| Tool | Use it for | When |
|---|---|---|
| **Superpowers** (`/superpowers:*`) | brainstorming → writing plans → executing plans → verification before completion | Planning each phase; before marking any phase done |
| **Last30days** | Research current e-commerce UI/UX trends (Reddit, X, HN, GitHub, Dribbble talk) | Before choosing the design direction |
| **Context7** (MCP) | Current docs for Django, Playwright-Python, pytest-django, pytest-html, Bootstrap 5, scikit-learn, GSAP, Lenis | Whenever writing code against a library API |
| **Hallmark** | Main design brain: study → design direction → audit | Design direction (Phase 1), every UI phase, and a full audit at the end |
| **GSAP skills** (gsap-core, gsap-timeline, gsap-scrolltrigger, gsap-performance) | Correct vanilla-JS GSAP/ScrollTrigger code + cleanup + performance | Any animation work |
| **Playwright MCP** | Open the running site, click through, take desktop + mobile screenshots, LOOK at them, fix | After every UI change; full sweep at the end |
| **Vercel Web Design Guidelines** | Final polish audit (accessibility, forms, focus, contrast, motion-reduce, performance) | UI polish phase and final |
| **Diagram Design** | Architecture + data-flow + recommender diagrams for README and CODE_MAP | Docs phase |
| **Humanizer** | Make README, on-site copy and product descriptions read naturally, not AI-written | Seed data + docs phase |

Not used (React-only or not needed): Next.js, shadcn, AI Elements, 21st.dev, React Bits, Motion (React), Langfuse, RAGAS, Scrapling.

## 4. Environment rules
- Project folder: `D:\Internship Projects\ai-multicategory-ecommerce` (Windows). Use a `.venv` in the project. Commands must work in **PowerShell**.
- `requirements.txt` with **pinned** versions. Do not install CUDA, torch, transformers or any LLM — none are needed.
- Playwright browsers: `python -m playwright install chromium` (one-time).
- Secrets and defaults in `.env` (loaded with python-dotenv or django-environ): `SECRET_KEY`, `DEBUG`, `ADMIN_USERNAME`, `ADMIN_PASSWORD`, `ADMIN_EMAIL`, email settings. Commit `.env.example` only. `.gitignore` must exclude `.env`, `.venv`, `db.sqlite3`, `media/uploads` (user uploads), `reports/` run output, `sent_emails/`, `__pycache__`.
- Never hardcode credentials in source. Default admin is created by a management command reading `.env`; README warns to change it before deployment.
- Git: commit after every completed phase with a clear message; push to `github.com/Krishna141414/ai-multicategory-ecommerce` when the owner has created the repo (ask once if the remote is missing).

## 5. Implementation rules (brief rules + how to satisfy them)
Field names in the brief are the contract — keep them (you may add extra fields, never remove brief ones).

**Auth & roles (Rule 1, 9)**
- Use Django's auth `User` for passwords (hashed). Customer profile model holds the brief fields (`name, email, mobile_number, address, registered_date, status`), linked one-to-one to `User`; customers log in with **email + password**, admin with **username + password**.
- Email unique (case-insensitive). New customers **Active** by default. Deactivated customers cannot log in (check status in the login flow, show a clear message).
- Role-based access: admin views require staff role; customer views require an authenticated active customer. Customers can never reach admin URLs and vice-versa. CSRF on every form. All input validated server-side (Django forms).

**Catalog (Rule 2)**
- Only admin can create/update/delete categories and products. Each product has one category. `price > 0`, `quantity >= 0` (DB constraints + form validation).
- Zero-stock products show "Out of stock" and cannot be added to cart.
- Deleting a product that has orders → **soft delete** (status inactive, hidden from listings) so history stays intact; products with no orders may be hard-deleted. Order rows also **snapshot** `product_name` (and price) so order history never breaks.
- Product has an extra `is_sponsored` flag (for the sponsored carousel) — admin toggle.

**Cart & checkout (Rule 4)**
- Multiple products per cart; cart quantity can never exceed available stock (validate on add AND on update AND again at submit).
- **Submit Cart** in ONE `transaction.atomic()` block: re-check stock with row locking (`select_for_update`), reserve (decrement) stock, create **one order row per cart item**, all sharing one generated `order_id`, each with its own `id`, `amount = price × quantity`, status **Pending**. Total = sum of amounts.
- Guard against duplicates: re-submitting the same cart / double-clicking must not create a second set of orders (reuse the existing pending, unpaid checkout or use an idempotency token).
- Cart items are cleared **only after successful payment confirmation**.

**Dummy payment (Rule 5)**
- No real gateway. Payment form lets the user simulate **Success** or **Failure** (e.g. a choice or a test card number), records a Payment row (`order_id, customer_id, total_amount, payment_method, payment_status, payment_date`).
- Success → all rows of that `order_id` become **Confirmed**, cart cleared, confirmation page shown, **order email** sent. Failure → orders NOT confirmed/paid, clear failure message, user can retry. Paying an already-paid order must not create duplicates or double-charge (idempotent).
- Admin cancelling an order restores its stock.
- Email: Django **file-based email backend** (`sent_emails/`) by default so it works offline; SMTP optional via `.env`. Email contains order id, items, quantities, amounts, total, status.

**Orders**
- Statuses exactly: Pending, Confirmed, Shipped, Delivered, Cancelled. Admin updates status; customer sees the updated status in order history/details.

**Ratings & reviews**
- Separate Rating (1–5) and Review (text) tables as in the brief. Only customers who purchased the product (delivered/confirmed) may rate/review — one rating per customer per product (can update). Product detail shows average rating.

**Queries / messages (Rule 6)**
- ONE messages table with the brief fields (`conversation_id, sender_id, sender_type, receiver_id, receiver_type, parent_message_id, subject, message, posted_date, status`). New conversation → `parent_message_id = NULL`, new `conversation_id`. Replies point to the parent and reuse the `conversation_id`. Customers see only their own conversations; admin sees all and can reply. Show a threaded conversation view.

**AI recommender (Rule 3) — runs locally, no paid API**
- Tables: `ProductFeature (product_id, category, product_name, brand, description, keywords, price)` and `CustomerProductInteraction (customer_id, product_id, interaction_type [view/cart/purchase], interaction_date)`.
- Pipeline in one clear module (e.g. `recommender/engine.py`): collect product info → preprocess with Pandas (lowercase, clean, combine category + name + brand + description + keywords; give name/category/keywords extra weight) → `TfidfVectorizer` → `cosine_similarity` matrix → cache it, rebuild when products change.
- **Similar products** (product page): top-N by similarity, excluding the product itself.
- **Personalised** ("Recommended for you"): build interests from viewed / carted / purchased products (weight purchase > cart > view, recent > old), aggregate similarities, exclude the interest products themselves, return top-N.
- Only **active, in-stock** products are recommended. **New customers** (no interactions) get popular (most ordered / best rated) or category-based suggestions.
- Every recommendation shows: name, category, image, price, **similarity score**, and a short "because you viewed X" reason.
- Log interactions automatically on product view, add-to-cart and purchase.

**Testing (Rules 7, 8)** — see BUILD_PROMPT Phase 10 for the full list
- Playwright **sync API** + Pytest + pytest-django's `live_server` on a **separate test database** — tests never touch the real `db.sqlite3`. (Set `DJANGO_ALLOW_ASYNC_UNSAFE=true` in the test setup if Playwright's loop triggers Django's async-safety check.)
- Controlled test data via fixtures/factories; every test independent (can run alone, in any order).
- Reliable locators only: `get_by_role`, `get_by_label`, `get_by_text`, `data-testid`. **No `time.sleep`** — use Playwright auto-waiting and `expect(...)`.
- Positive AND negative cases. E2E tests check visible behaviour AND persisted results (DB). Checkout tests assert correct totals. AI tests assert relevance (same category / shared keywords / score ordering).
- Screenshot on every failure (saved under `reports/screenshots/`). HTML report via pytest-html (`reports/report.html`). Headed and headless both supported (`--headed`, `--slowmo`).
- Test cases are catalogued (`id, test_name, module, test_description, expected_result`) and each run records executions (`test_case_id, execution_date, actual_result, status, execution_time, screenshot_path`) and a summary (`execution_date, total_tests, passed_tests, failed_tests, skipped_tests, total_execution_time, report_path`) into a **separate reports store** (not the shop's business data), shown on the Admin "Test Reports" page.

## 6. UI rules
- Bootstrap 5 is the base grid/components, but with a fully custom design system on top (CSS variables for colours, type scale, radius, shadows, spacing). It must not look like stock Bootstrap.
- Pages must be responsive (mobile, tablet, desktop). Respect `prefers-reduced-motion`. Visible focus states, proper labels, good contrast.
- Empty states, loading/skeleton states, success/error toasts, and form error messages for every flow.
- Every important element gets a stable `data-testid` for the tests.
- After every UI change: run the server, check it with Playwright MCP screenshots (desktop 1440 px + mobile 390 px), fix what looks off.

## 7. Working style
- Follow `BUILD_PROMPT.md` phase by phase; do not skip steps or merge phases silently.
- Use **Context7** before writing library-specific code. Use **Superpowers** to plan each phase and verify before marking it done.
- Keep `PROGRESS.md` updated after every step (done / in progress / next / blockers). If context is running low, update `PROGRESS.md`, commit, and stop cleanly so the next session can resume.
- Keep `docs/REQUIREMENTS_MATRIX.md` updated: every brief item → where it is implemented → which test covers it → status.
- Record design/architecture choices in `docs/DECISIONS.md` (short: decision + reason).
- Never claim something works without running it. Run the server and the relevant tests before ticking a step.
- Code style: clear names, small functions, docstrings on main functions, no dead code, no giant views — put business logic in services (cart/checkout/payment/recommender).
