# Hallmark audit (Phase 9.6)

Date: 2026-11-11. Target: the Velora storefront and admin (`templates/`, `static/css/`, `static/js/`), against
`docs/DESIGN_SYSTEM.md` (Hallmark Editorial theme). Tool: Hallmark `sloplint.mjs` (v2.0.0) on the stylesheets and
templates, plus five live routes (`/`, `/category/electronics/`, `/product/sonvale-arc-3-wireless-earbuds/`,
`/ai/explainer/`, `/account/login/`). The linter's render tier could not run (no puppeteer on this machine), so the
judged gates were walked from our own Playwright screenshots (`screenshots/sweep/`, `screenshots/phase9/`).
Raw output: `.hallmark/before.txt` and `.hallmark/after.txt` (git-ignored).

## The read

- **What the site is for:** shoppers buying everyday products across ten aisles; the one action is *add to cart*.
- **What works and stays:** the editorial system (ink buttons, hairline/heavy rules, condensed heads over a serif lead,
  green only as a signal); real product photos everywhere; the sponsored strip and quick view as the signature;
  ruled lists instead of boxed cards; the admin ledger.
- **What read as generated:** two eyebrows over headings, four tracked-capital labels, a side stripe on unread rows.
- **What was broken:** `100vw` widths on three floating layers (scrollbar overflow), the quick-view button hidden at
  rest with no way to appear without scripting, colour literals in two mask gradients, raw spacing values.

## Findings and what was done

| Gate | Tier | Where | Finding | Done |
|---|---|---|---|---|
| 34 | Floor | `base.css` `.toast-stack`, `.confirm-dialog`; `store.css` `.qv-panel` | `calc(100vw - …)` widths overflow by the scrollbar | Now `calc(100% - …)` |
| 48 | Floor | `store.css` `.category-rail`, `.sponsored-viewport` | `#000` literal in mask gradients | Lifted to `--mask-solid` in `tokens.css` |
| 50 | Floor | product, category, quick-view and confirmation heads | Display heads with long names had no wrap rule | `h1, h2, h3, .qv-name { overflow-wrap: break-word; min-width: 0 }` in `base.css` |
| 54 | Floor | `core/home.html`, `recommender/explainer.html` | Eyebrow above the `<h1>` | Removed; the headings already say it |
| 67 | Floor | `.eyebrow`, `.xp-label`, `.hero-offer-label`, `.sp-tag` | Uppercase, tracked labels | Body face, a step smaller, sentence case, untracked; `.eyebrow` deleted |
| 62 | Floor | `store.css` `.qv-trigger` | Hidden at rest, needs a script to appear | Visible by default; tucked away only for mouse users with scripting (`.js` class set in `<head>`); hidden entirely without JS, where it would do nothing |
| 24a | Floor | `base.css` `.form-select`, `store.css` tab bar | Raw `2.5rem` / `64px` where tokens exist | `var(--space-xl)`; new `--tabbar-h` token used in all five tab-bar offsets |
| 13 / 58 | Floor | home hero | Lead was two sentences, 30 words | "Ten aisles of everyday things, every price shown beside its MRP." |
| 3 | Reflex | `admin.css` `.inbox-row.is-unread` | Side stripe on unread rows | An 8px accent square before the subject, as on the customer queries list |
| 26b | Reflex | small controls | No pressed state outside `.btn` | `:active` nudge on `.icon-btn`, `.qv-trigger`, `.mega-toggle`, `.header-link`, rail links, Explainer step buttons |
| F6 | Finish | `.price` | Prices without tabular figures | `font-variant-numeric: tabular-nums` on `.price` |

## Kept on the record (not changed, with the reason)

| Gate | Finding | Why it stays |
|---|---|---|
| 48 | Inline hex colours in `templates/emails/order_confirmation.html` | Email clients ignore CSS variables and OKLCH; inline hex is the only way an HTML email keeps the brand (DECISIONS, Phase 6). The plain-text part carries the same content. |
| 56 | "Two sticky top:0 elements" in `admin.css` | False positive: `.admin-sidebar` (column 1) and `.admin-topbar` (column 2) sit side by side, never stacked, and `.site-header` is never on an admin page. |
| 26a, 34 (×105) | "No `:focus-visible`" / "no `overflow-x: clip`" on each template | False positive: the linter reads each template alone. `base.css` (loaded by every page through `base.html`) has `:focus-visible` on every control and `overflow-x: clip` on `html, body`. |
| 11 | Product images scale to 1.04 on hover | Owner-requested motion, written into DESIGN_SYSTEM §7 item 1 (and DECISIONS, 2026-11-07). |
| F24 | Hairline border plus soft shadow on floating layers | The design system's one permitted elevation: floating layers (dropdown, mega menu, quick view, toast, modal) carry `--shadow-pop` together with a 1px ink border. |
| 42 | Footer has four link columns | Decided: the "mast" footer (wordmark over the links) named in the stamp; four columns hold the ten aisles, the account and the AI pages. |

## Judged gates (from the screenshots)

- **12, hero above the fold:** at 1280 x 800 the headline, lead and primary action end at y = 691. Pass.
- **14, capped container:** at 1920 the hero is 1440 px wide and centred; only the gutters grow. Pass.
- **8, invented facts:** none. Every number on the site comes from the database (prices, MRP, stock, ratings, order
  counts, similarity scores); "Best sellers" is computed from orders.
- **9, eyebrows and tracked labels:** none left.
- **10, middle dots and glued arrows:** none.
- **11, gradients, cards in cards, emoji icons:** none; icons are Bootstrap Icons.
- **7, reduced motion and no-script:** reveals, the sponsored drift, the Explainer animation, quick view and the star
  picker all have a reduced-motion path; every page's content is visible without JavaScript.

## Result

Stylesheets: **Floor 1 FAIL** (56, a false positive explained above) · **Reflex 0** · 9 warnings kept with reasons
(was 132 FAIL / 82 REFLEX on the first run, most of them the per-template false positives).
