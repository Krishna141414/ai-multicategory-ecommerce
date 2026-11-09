# Decisions

Short log of design and architecture choices (decision → reason). Newest at the bottom of each section.

## Architecture
- **9 apps** (core, accounts, catalog, orders, reviews, messaging, recommender, adminpanel, testreports) with business logic in service modules. → Each file maps to one brief area, which makes the video walkthrough easy and keeps views thin.
- **Custom admin UI at `/manage/`**, not Django's `/admin`. → The brief asks for an admin side as part of the product; Django admin stays disabled so there is one admin path to test.
- **Customer profile = `Customer` model linked 1:1 to Django `User`.** → Brief fields live in one table; passwords stay in Django's hashed `User.password`.
- **Email login via a custom auth backend; username = email for customers.** → Brief says customers log in with email + password, admin with username + password.
- **Test reports in a second SQLite DB (`reports.sqlite3`) via a DB router.** → Rule: tests must not modify production data; the reports store is separate from shop data.
- **Results recorder writes JSON, then `manage.py record_test_run` runs in a subprocess at session end.** → Under pytest every DB alias points to a test DB; a subprocess uses the real settings, so results land in the real reports DB.
- **Test DB is a file (`test_db.sqlite3`), not in-memory.** → `live_server` runs in another thread; a file DB with IMMEDIATE transactions avoids shared-cache locking issues.

## Checkout & stock
- **SQLite `transaction_mode=IMMEDIATE` + conditional `F()` decrement + `select_for_update()`.** → `select_for_update` is a no-op on SQLite (Django docs); IMMEDIATE takes the write lock at BEGIN, and `filter(quantity__gte=q).update(...)` can never oversell.
- **Duplicate guard = `checkout_key` (uuid rendered into the checkout form, stored on each order row).** → A double-click or re-POST returns the existing order_id instead of creating new rows.
- **Older unpaid Pending checkouts are cancelled (stock restored) when the customer submits a new cart.** → Prevents abandoned checkouts from holding stock forever; documented and tested.
- **Order status transitions:** Pending→Confirmed|Cancelled, Confirmed→Shipped|Cancelled, Shipped→Delivered; Delivered and Cancelled are final. Cancel restores stock. → Avoids double stock restores and nonsense moves (e.g. Delivered→Pending).
- **Category delete is blocked while the category still has products.** → Every product must belong to one category (Rule 2); deleting silently would orphan or cascade-delete history.

## Recommender
- **Engine cached in memory, keyed by a fingerprint (feature count + latest product update).** → Rebuilds automatically after admin edits without signals racing; `build_recommender` forces a rebuild.
- **Weights: name ×3, keywords ×3, category ×2, brand ×1, description ×1; interactions purchase 3 > cart 2 > view 1 with 14-day half-life.** → CLAUDE.md asks for extra weight on name/category/keywords and purchase > cart > view, recent > old.
- **New-customer fallback shows a "Popularity" score instead of pretending it is a similarity score.** → Honest labelling; still shows a score as the brief requires.

## Design (Phase 1.2, Hallmark)
- ~~Store name "Chowk"~~ → **renamed "Velora" (owner request, 2026-11-09).** Shown everywhere users see the brand via `settings.STORE_NAME`; code identifiers (modules, folders, the `window.Chowk` JS namespace) were left unchanged on purpose. Wordmark width opened from `wdth` 75 to 82 so the V and the round letters don't look cramped.
- **Hallmark theme Editorial** (dealt 2 of 3; Atelier and Carnival rejected). → A catalogue of 110 products needs a confident print-catalogue voice that frames product photos; Atelier is too hushed/luxury for electronics and toys, Carnival too loud for dense listings and an admin side.
- **Ink primary buttons, green only as a signal (<5% of a screen).** → Keeps the store from looking like a stock Bootstrap/SaaS template; green carries meaning (in stock, focus, sponsored).
- **Square corners, hairline rules, no card shadows.** → The theme's material; immediately distinct from default Bootstrap's rounded cards.
- **Bricolage Grotesque (condensed 800 heads, 500 UI) + Source Serif 4 for reading.** → Two families, both OFL, self-hostable; condensed heads give the catalogue voice, serif makes descriptions/reviews read like copy, not UI.
- **Status colours added (danger/warn/info/star) beyond the theme.** → An e-commerce app needs order statuses and ratings; all measured ≥ 4.5:1 (stars ≥ 3:1 as icons).
- ~~Motion limited to a few exceptions to the theme's "state only" rule.~~ Superseded (owner feedback, 2026-11-07): see below.
- **Motion widened to "tasteful, purposeful" (owner request, 2026-11-07).** Product-card hovers, quick view, add-to-cart button state + badge bump, toasts, skeleton loaders, subtle scroll reveals, smooth sponsored carousel, nav/dropdown transitions, Explainer animations, Lenis on storefront pages. → The owner wants good UI with tasteful motion, not a near-static page; the Editorial look (type, rules, palette) stays, only its motion posture changes. Limits: transform/opacity only, ≤ 600ms, no parallax/bounce/glow, full `prefers-reduced-motion` fallback, no reveals in admin.
- **Django serves /media/ in all modes.** → Local-only demo (rule 10) and the test live server runs with DEBUG=False; a real deployment would put media behind a web server.

## Images (Phase 2.5, revisited 2026-11-09)
- **Owner-supplied photos for 10 products** (9 AI-generated by the owner, 1 from Pexels), imported with `scripts/import_manual_photos.py` and credited as such. → Openverse/Wikimedia had no clean, logo-free match; Pexels paused new API keys.
- **Fictional brand labels printed onto plain packaging** (11 photos) with `scripts/brand_labels.py`; originals kept in `media/products/originals/`; each result checked by eye. → A blank tube labelled "Dewlab SPF 50" reads as the real listing and keeps the "fictional brands only" rule visible in the photos. Ink is multiplied into the photo's shading so it looks printed, not pasted.
- ~~3 products keep the placeholder (soundbar, watch, microwave).~~ Updated 2026-11-09: the owner's soundbar, smartwatch and microwave photos are in. Only the Thread & Thali analog watch keeps the placeholder (the owner's smartwatch photo went to the Orvia smartwatch it actually shows).

## Typography in the UI (Phase 3)
- **Bricolage Grotesque is the body/UI default; Source Serif 4 is used for reading text** (`.prose`, `.lead`, descriptions, reviews, messages). → A store is mostly controls, prices and short labels; Hallmark's app-screen rule allows the UI face there, while the serif keeps the editorial voice where people actually read.

## Cart, payment and orders (Phase 6)
- **Add to cart and quantity changes use fetch + JSON, with the same forms posting normally without JavaScript.** → The page does not reload for every click, and the flow still works (and is testable) with JS off.
- **Cart lines are cleared only after a successful payment; a failed payment leaves the order Pending and the cart intact.** → Brief Rule 4/5: the customer can retry, and nothing is confirmed or charged on failure.
- **The simulated outcome is an explicit "Result to simulate" choice marked "Demo only".** → Honest for a demo store and easy to show both paths on video; no fake card numbers to remember.
- **Order email is rendered from text + HTML templates and sent with `transaction.on_commit`.** → No email goes out if the payment transaction rolls back. The HTML version uses inline hex colours because email clients ignore CSS variables and OKLCH.
- **On phones the checkout and confirmation tables drop the unit Price column (Qty and Amount stay).** → Keeps the 16 px gutter at 390 px without a horizontally scrolling table; the unit price is still on the order detail page.
