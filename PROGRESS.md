# PROGRESS.md

Claude Code updates this after every step. A new session reads it first and continues from "Next".

## Status
- Current phase: Phase 4 — Admin panel
- Last completed step: Gate 3 passed
- Next: 4.1 Admin dashboard

## Next — Phase 4 (admin panel, custom UI at /manage/)
Start 4.1 Dashboard: real totals (total_customers, total_categories, total_products, total_orders = distinct order_id, total_sales = paid, not cancelled), recent orders table, 14-day inline-SVG chart; pass `section` to admin templates. Admin shell: `templates/adminpanel/base.html` (sidebar links appear automatically once `adminpanel:<name>` URLs exist). Shared form/badge/table styles are in `static/css/base.css`; admin layout in `static/css/admin.css`. Follow docs/plans/implementation-plan.md Phase 4.

## Log
| Date | Step | Result / notes |
|---|---|---|
| 2026-11-07 | 0.1 Toolkit | All present: Superpowers, Last30days, Diagram Design (plugins/skills); Playwright MCP + Context7 MCP connected; Hallmark, GSAP skills (core/timeline/scrolltrigger/performance/utils/plugins), web-design-guidelines, Humanizer (global skills). Env: Python 3.14.0, Node 24.11.1, Git 2.52. The claude.ai Vercel MCP needs auth but is not required (the Vercel guidelines are used via the skill). |
| 2026-11-07 | 0.2 Matrix | docs/REQUIREMENTS_MATRIX.md: 215 rows across stack, admin, customer, categories, AI, test cases, E2E, reporting, rules 1–10, extras. |
| 2026-11-07 | 0.3 Research | Last30days run (Reddit/HN/GitHub; X+YouTube not configured, Reddit search partly blocked so community signal thin) + 3 web supplements (Baymard etc.). 11 patterns saved to docs/research/ui-trends.md. |
| 2026-11-07 | 0.4 Context7 | Docs pulled for Django 6.1, pytest-django, Playwright-Python, pytest-html, scikit-learn, Lenis/GSAP. Key finding: select_for_update is a no-op on SQLite → use IMMEDIATE transaction mode + conditional F() decrement. Notes + versions in docs/research/library-notes.md. |
| 2026-11-07 | 0.5 Venv | Python 3.14 .venv; requirements.txt pinned (Django 6.1.3, scikit-learn 1.9.1, pandas 3.1.1, pytest 9.2.0, playwright 1.64.1 …); installed OK; Chromium installed. |
| 2026-11-07 | 0.6 Git | git init (main), .gitignore, .env.example, origin = github.com/Krishna141414/ai-multicategory-ecommerce (exists, empty). |
| 2026-11-07 | 1.1 Plan | Brainstorming: spec fixed by brief + CLAUDE.md, owner asked to proceed without questions. writing-plans → docs/plans/implementation-plan.md (apps, models, service interfaces, algorithms, tests per phase, review focus). Decisions logged in docs/DECISIONS.md. |
| 2026-11-07 | 1.2 Design | Hallmark deal → Editorial theme. Store name Chowk. docs/DESIGN_SYSTEM.md (OKLCH tokens, contrast measured: all text ≥ 4.5:1, UI ≥ 3:1), Bricolage Grotesque + Source Serif 4, spacing/radius/shadow/z scales, Bootstrap Icons, motion principles + exceptions. Reasons in DECISIONS.md. |
| 2026-11-07 | 1.3 Pages + Gate 1 | docs/plans/pages.md: 21 customer + 17 admin pages with URL and purpose. Gate 1 passed: plan, design system, page inventory written and committed. |
| 2026-11-07 | 2.1 Scaffold | config/ + 9 apps; settings read .env (python-dotenv); 2 SQLite DBs (default IMMEDIATE txn, reports) + router; static/media; file email backend → sent_emails/; role decorators, ActiveCustomerMiddleware, context processor. manage.py check: no issues. |
| 2026-11-07 | 2.2 Models | All brief fields + extras (mrp, is_sponsored, slug, checkout_key, payment reference). DB constraints: price>0, qty>=0, mrp>=price, cart qty>=1, rating 1–5, unique lower(email), one success payment per order. Migrations clean on default + reports DB (testreports tables only in reports.sqlite3). tests/unit/test_models.py 5 passed. Email moved to Django 6.1 MAILERS. |
| 2026-11-07 | 2.3 Vendor | static/vendor/: Bootstrap 5.3.8, Bootstrap Icons 1.13.2, GSAP 3.15.1 (+ScrollTrigger, Flip), Lenis 1.3.27; static/fonts/: Bricolage Grotesque + Source Serif 4 variable woff2 (latin + latin-ext for ₹) with OFL licences. grep shows no CDN URLs; source-map comments stripped. |
| 2026-11-07 | 2.4 Seed | catalog/seed_data.py: 10 brief categories × 11 products = 110, fictional brands (Sonvale, Lumora, Orvia, Corelane, Tadka Home …), ₹ prices with optional MRP, 8 out of stock, 11 sponsored, keyword-rich descriptions; Humanizer pass (removed 'actually', closers, aphoristic category copy). core/demo.seed_catalog + seed_demo command: idempotent (ran twice → 10/110). |
| 2026-11-07 | 2.6 Commands | create_default_admin (from .env, keeps existing password unless --reset-password), seed_demo (catalogue + 4 customers + 9 past orders/20 rows + 8 payments + 14 ratings + 11 reviews + 2 conversations + 31 interactions + 2 cart items; idempotent), reset_demo (flush shop DB only, confirm with RESET or --yes). Note: 2.6 completed while 2.5 image download is still running. |
| 2026-11-07 | 2.5 Images | 98/110 real photos (Openverse, Wikimedia Commons; CC0/PDM/CC BY/CC BY-SA), each checked by eye for product match and real logos; square 900 px JPEGs in media/products/ (9.3 MB); wide shots padded, one router photo edited to remove the maker's name; credits in docs/IMAGE_CREDITS.md. 12 placeholders pending the owner's manual Pexels photos (Pexels has paused new API keys). |
| 2026-11-07 | Gate 2 | migrate (both DBs), create_default_admin, seed_demo run cleanly and idempotently; shell counts 10 categories / 110 products / 4 customers / 9 orders; manage.py check clean; 7 unit tests pass. Motion posture widened per owner request (DESIGN_SYSTEM §7, DECISIONS). |
| 2026-11-09 | 2.5 Photos + labels | 10 owner photos imported (9 AI-generated by Krishna, 1 Pexels/Kindel Media) via scripts/import_manual_photos.py; fictional brand labels printed on 11 plain-packaging photos via scripts/brand_labels.py (originals in media/products/originals/, every result checked by eye, 3 placements corrected); IMAGE_CREDITS.md updated; 107/110 products with photos, 3 placeholders. Motion posture already widened (DESIGN_SYSTEM §7). Gate 2 re-checked: check clean, 7 unit tests pass. |
| 2026-11-07 | 3.1 Customer auth | templates/base.html + partials (header, footer, tab bar, toasts, field), accounts EmailBackend, RegistrationForm (unique email ci, 10-digit mobile normalised, Django password validators), CustomerLoginForm, register/login/logout (POST-only) views. Browser: registered Kavya → signed in + toast; logout via account menu. |
| 2026-11-07 | 3.2 Admin auth | /manage/login/ (username + password, staff only; wrong password or customer account → same 'Username or password is incorrect.'), POST logout, admin shell (sidebar + top bar) and dashboard stub; admin.css app-scale. Browser: invalid + valid admin login checked. |
| 2026-11-07 | 3.3 Roles | login_error_for shows 'Your account has been deactivated…' only with the right password; set_customer_status keeps User.is_active in sync; ActiveCustomerMiddleware; customer_required/admin_required. Browser: deactivated Rahul blocked with message; customer on /manage/ → 403 page. |
| 2026-11-07 | 3.4 Profile | Profile page (all brief fields + status badge) and edit form (server-side validation, email unique ci, User.username/email kept in sync). tests/unit/test_auth.py: 17 tests; all 24 unit tests pass (fast MD5 hasher in tests only). |
| 2026-11-07 | Gate 3 | Every auth path verified in the browser with Playwright MCP (screenshots in screenshots/gate3/, 1440 + 390): register, login, invalid login, deactivated login, logout, admin invalid/valid login, customer→admin 403. Fixed: shared form styles moved to base.css (admin login), cache-busting ?v= on CSS/JS, aria-labels on icon-only header links on mobile. Category bar overflows at 1440 → mega menu in 9.1. |

## Pending owner actions / follow-ups
- **3 placeholders left:** soundbar, watch, microwave. If Krishna adds soundbar.jpg / watch.jpg / microwave.jpg to `media/manual_photos/`, add them to `PHOTOS` in `scripts/import_manual_photos.py`, run it, add labels in `scripts/brand_labels.py` if the packaging is plain (check by eye), update `docs/IMAGE_CREDITS.md`, run `python manage.py seed_demo`.

## Blockers / questions for Krishna
- (none)

## Decisions made (short; details in docs/DECISIONS.md)
- (none yet)
