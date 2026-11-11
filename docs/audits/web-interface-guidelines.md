# Web Interface Guidelines audit (Phase 9.6)

Date: 2026-11-11. Rules: Vercel Web Interface Guidelines, fetched fresh from
`vercel-labs/web-interface-guidelines/main/command.md`. Scope: `templates/`, `static/css/`, `static/js/` and the form
widgets in `*/forms.py`. React-only rules (hydration, `useState`, `Link`) were applied in their plain Django/HTML
meaning. Every page was also re-checked in the browser at 1440 and 390 px after the fixes (`screenshots/sweep/`):
no horizontal overflow, no console errors.

## Fixed

static/css/store.css:474 - `.xp-step h2 { outline: none }` on the Explainer's focused headings → removed; the global `:focus-visible` ring applies
templates/base.html:5 - no `<meta name="theme-color">` → added, matches `--color-paper`
static/css/base.css (end) - no `touch-action: manipulation` on controls → added for a, button, input, select, textarea, label, summary
static/css/base.css (end) - tap highlight not set → a 12% ink tint, set on `html`
static/css/base.css (end) - no `overscroll-behavior: contain` on floating layers → `.qv-panel`, `.mega-menu`, `.dropdown-menu`, `.modal-body`, `.confirm-dialog`
templates/partials/header.html:4, footer.html:4, adminpanel/base.html:12, adminpanel/login.html:12 - brand name could be machine-translated → `translate="no"`
accounts/forms.py:42, 92, 115, 144 - email and username fields spell-checked → `spellcheck="false"` (username also `autocapitalize="none"`)
templates/adminpanel/*/list.html, queries/inbox.html - search placeholders did not end with `…`, and invited autofill → `…` added, `autocomplete="off"`
catalog/forms.py:20 - search placeholder → "Product, brand or keyword…"

Also fixed in the same pass (found by the Hallmark audit, `hallmark-audit.md`): `100vw` widths on three floating layers,
eyebrows, tracked-capital labels, the quick-view button hidden at rest, raw spacing values, tabular figures on prices,
and admin list pages that widened the page on phones.

## Checked and passing

- Accessibility: icon-only buttons have `aria-label` (sponsored prev/pause/next, quick-view close, toast close, quantity
  steppers, password toggles); every field has a `<label>`; decorative icons are `aria-hidden="true"`; toasts and the
  Explainer status are `aria-live="polite"`; product images have `alt="{name} by {brand}"`, decorative ones `alt=""`;
  one `<h1>` per page; skip link to `#main`; `scroll-margin-top` / `scroll-padding-top` clear the sticky header.
- Focus: global `:focus-visible` ring (2px, focus colour, instant); `:focus-within` on cards, the star picker and the
  payment choices; sticky header and the phone tab bar never cover a focused control (`scroll-padding-top` and
  `scroll-padding-bottom`, verified in Gate 7).
- Forms: correct `type`/`inputmode` (email, tel, number, search); autocomplete tokens on every personal field
  (name, email, tel, street-address, new-password, current-password, username); no paste blocking; labels wrap or
  point at their controls; errors are inline next to each field; submit buttons stay enabled until the request starts,
  then show "Adding…" / "Placing order…" / "Sending…".
- Animation: transform and opacity only; no `transition: all`; every animation has a reduced-motion path; the sponsored
  strip (autoplay longer than 5 s) has a visible pause button and pauses on hover, focus and off-screen; the Explainer
  autoplay has Pause.
- Typography: `…` everywhere (no `...`); headings use `text-wrap: balance`, paragraphs `pretty`; prices and number
  columns use tabular figures.
- Content handling: long names wrap (`overflow-wrap: break-word; min-width: 0` on heads); grid tracks are
  `minmax(0, 1fr)`; every list has an empty state.
- Images: every `<img>` has `width` and `height`; below-the-fold images are `loading="lazy"`; the hero deal image has
  `fetchpriority="high"`.
- Performance: fonts are self-hosted with `font-display: swap` and the main face preloaded; no CDN, so no preconnect
  needed; the quick-view fragment is fetched once per product and cached.
- Navigation and state: search filters, sort and pagination live in the query string; every navigation is an `<a>`;
  destructive actions (admin delete, deactivate, cancel order, and removing a cart line) go through a confirmation dialog.
- Zoom: no `user-scalable=no` or `maximum-scale`.
- Theming: `color-scheme: light` declared; native selects have explicit background and text colours.

## Kept on purpose (with the reason)

- **Sentence case, not Title Case**, for headings and buttons: the design system (Editorial theme, Hallmark floor)
  sets every label in sentence case; mixing the two would read as two products.
- **"We" in a few store messages** ("We've emailed the details", "We'll reply here"): the store speaking for itself is
  the usual shop voice; instructions to the shopper are in the second person.
- **Dates and prices are formatted on the server** (Django `date` filter, the `inr` filter) rather than with
  `Intl.*` in the browser: the pages are server-rendered for one locale (en-IN, ₹), so there is nothing to hydrate
  or mismatch.
- **`autofocus` on the sign-in email and admin username:** the sign-in page has one job and one primary input.
- **The Explainer's current step is not in the URL:** the chosen product is (`?product=<id>`); the step is a few seconds
  of reading, and every step is also visible stacked without JavaScript.
