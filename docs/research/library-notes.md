# Library notes (Context7, 2026-11-07)

Docs pulled with Context7 before writing code. Versions are the latest stable on PyPI/npm today; they are pinned in `requirements.txt` and in `static/vendor/README.md`.

## Python (pinned)
| Package | Version | Why |
|---|---|---|
| Django | 6.1.3 | Web framework (auth, forms, ORM, CSRF, email) |
| scikit-learn | 1.9.1 | `TfidfVectorizer`, `cosine_similarity` |
| pandas | 3.1.1 | Product-text preprocessing |
| numpy | 2.5.4 | Matrix ops (scikit-learn dependency) |
| Pillow | 13.0.0 | `ImageField` uploads |
| python-dotenv | 1.2.4 | Load `.env` |
| pytest | 9.2.0 | Test runner |
| pytest-django | 4.14.0 | `live_server`, test DB |
| pytest-playwright | 0.10.0 | `page` fixture, `--headed`, `--slowmo` |
| playwright | 1.64.1 | Browser automation (sync API) |
| pytest-html | 4.2.0 | HTML report |
| pytest-randomly | 5.0.0 | Random order runs (rule check 10.9) |

## Front-end (downloaded once into `static/vendor/`, no CDN at runtime)
Bootstrap 5.3.8 · GSAP 3.15.1 (+ ScrollTrigger) · Lenis 1.3.27 · Bootstrap Icons 1.13.2 (subset used) · fonts self-hosted (woff2).

## What the docs told us (and how we use it)

**Django — `select_for_update()` is a no-op on SQLite.** The docs say SQLite ignores it (no error). So the checkout service does three things together:
1. calls `select_for_update()` anyway (correct on any other DB, and it documents intent),
2. sets SQLite `OPTIONS["transaction_mode"] = "IMMEDIATE"` (Django ≥ 5.1) so an `atomic()` block takes the write lock at BEGIN, which serialises concurrent checkouts,
3. decrements stock with a conditional update: `Product.objects.filter(pk=..., quantity__gte=qty).update(quantity=F("quantity") - qty)`; if it updates 0 rows, the whole transaction rolls back with a "not enough stock" error.

**Django — `F()` expressions** do relative updates without race conditions (used for stock and restore-on-cancel).

**Django — email.** `django.core.mail.backends.filebased.EmailBackend` + `EMAIL_FILE_PATH` writes each message to a file; we point it at `sent_emails/`. SMTP is opt-in from `.env`.

**pytest-django — `live_server`** runs the dev server in a thread and depends on `transactional_db`, so the DB is flushed between tests; data must be created per test (function-scoped fixtures/factories). Test DB is separate from `db.sqlite3`.

**Playwright pytest plugin** gives `page`, `context`, `new_context` (multi-user tests), and CLI flags `--headed`, `--slowmo`, `--screenshot only-on-failure`, `--tracing retain-on-failure`. Locators: `get_by_role`, `get_by_label`, `get_by_text`, `get_by_test_id` (reads `data-testid`). Assertions with `expect(...)` auto-wait. Playwright's sync API runs an event loop in the main thread, so Django's async-safety check needs `DJANGO_ALLOW_ASYNC_UNSAFE=true` in the test setup.

**pytest-html** — `--html=reports/report.html --self-contained-html`; add screenshots on failure in a `pytest_runtest_makereport` hookwrapper with `pytest_html.extras.image(...)`; set the title in `pytest_html_report_title`.

**scikit-learn** — `TfidfVectorizer(stop_words="english", ngram_range=(1, 2), sublinear_tf=True, min_df=1)`; rows are L2-normalised by default, so `cosine_similarity(X)` equals the dot product. `get_feature_names_out()` gives term names for the AI Explainer.

**Lenis + GSAP ScrollTrigger** — `lenis.on("scroll", ScrollTrigger.update)`, drive `lenis.raf(time*1000)` from `gsap.ticker`, `gsap.ticker.lagSmoothing(0)`. Lenis is only enabled when the user does not prefer reduced motion.
