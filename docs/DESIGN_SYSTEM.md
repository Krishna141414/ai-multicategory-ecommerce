# Design system: Velora

Decided with Hallmark (theme dealt: **Editorial**, 2/3, seed `multi-category-indian-online-store-e661·2b0b2b23·2026-11-07·r0`, genre editorial) and the patterns in `docs/research/ui-trends.md`. Reasons are in `docs/DECISIONS.md`.

## 1. Brand

- **Name:** **Velora** (renamed from the working name "Chowk" on 2026-11-09 at the owner's request). A coined, easy-to-say name with no meaning to explain: it reads as a store, not a product, and holds ten categories under one roof.
- **Wordmark:** "Velora" set in Bricolage Grotesque 800 at `wdth` 82 with tracking −0.005em (the open V and the round o–r–a need a little more width than the old condensed setting), ink. No logo glyph, no icon.
- **Personality:** a well-edited department-store catalogue. Exact, calm, a little literary, never shouty. It names the thing, the price and the delivery date. It does not say "amazing deals!!!".
- **Voice rules:** verbs on buttons ("Add to cart", "Place order", "Pay ₹4,598", "Remove item"); sentence case everywhere; no exclamation marks; no emoji; errors say what happened and what to do; empty states say what's empty and give one action.

## 2. Colour (OKLCH, light theme; posture: Restrained)

All colour goes through these tokens in `static/css/tokens.css`. Nothing past the token block uses a literal colour.

| Token | Value | Use | WCAG contrast on paper (measured) |
|---|---|---|---|
| `--color-paper` | `oklch(97% 0.007 86)` | page background (warm white, uncoated stock) | — |
| `--color-paper-2` | `oklch(94% 0.010 86)` | wells: filter column, order summary, footer | — |
| `--color-paper-3` | `oklch(91% 0.012 84)` | image backdrops, skeletons, table hover | — |
| `--color-ink` | `oklch(16% 0.012 280)` | headings, primary buttons, prices, ink band | 17.8:1 |
| `--color-ink-2` | `oklch(29% 0.011 280)` | body text | 13.0:1 |
| `--color-muted` | `oklch(48% 0.010 75)` | captions, meta, helper text | 6.0:1 |
| `--color-rule` | `oklch(85% 0.009 85)` | 1px hairlines between rows/cards | — |
| `--color-rule-2` | `oklch(64% 0.010 80)` | input borders, table-head rule (3:1 UI) | 3.1:1 (inputs keep a paper background; on paper-2 it is 2.8:1) |
| `--color-accent` | `oklch(49% 0.130 152)` | printer's green: in-stock, links on hover, one tag, focus | 5.4:1 |
| `--color-accent-ink` | `oklch(98% 0.005 88)` | text on green | 5.6:1 on accent |
| `--color-focus` | `oklch(52% 0.135 152)` | focus ring (2px outline, offset 2px) | ≥ 3:1 |
| `--color-danger` | `oklch(50% 0.170 27)` | errors, out of stock, cancelled | 6.0:1 (5.4:1 on its wash) |
| `--color-warn` | `oklch(52% 0.110 65)` | pending, low stock | 5.2:1 (4.7:1 on its wash) |
| `--color-info` | `oklch(46% 0.070 250)` | shipped | 6.5:1 |
| `--color-star` | `oklch(62% 0.150 65)` | rating stars (icons, 3:1 rule) | 3.5:1 |
| `--color-danger-wash`, `--color-warn-wash`, `--color-accent-wash`, `--color-info-wash` | same hue, L 94%, chroma 0.03 | status badge backgrounds | — |

Rules
- Green stays under 5% of any screen. **Primary buttons are ink, not green.** Green marks: "In stock", link hover underline, focus ring, the "Sponsored" tag, the active filter chip, the success toast edge.
- Never a gradient (except a 2-stop ink scrim under text on a photo), never a glow, never purple/blue SaaS tones.
- Status badges: text in the status colour on its wash, square, label face. Order statuses: Pending → warn, Confirmed → accent, Shipped → info, Delivered → ink on paper-3, Cancelled → danger.
- Never red and green as the only signal: every status also has its word.

## 3. Typography (self-hosted woff2, OFL)

| Role | Face | Setting |
|---|---|---|
| Display / headings (`h1`–`h3`) | **Bricolage Grotesque** variable | 800, `font-variation-settings: "wdth" 75, "opsz" 96`, tracking −0.012em, line-height 0.95–1.05, sentence case, `text-wrap: balance` |
| Prices, figures | Bricolage Grotesque | 800 condensed, `tabular-nums lining-nums` |
| UI labels, nav, buttons, inputs, tables, product names on cards, badges | Bricolage Grotesque | 500 (600 for emphasis), `"wdth" 100, "opsz" 12`, sentence case, untracked |
| Reading text (descriptions, reviews, messages, standfirsts) | **Source Serif 4** variable | 400 / italic 400, optical size auto, 17–18px, line-height 1.55, measure ≤ 70ch |

Type scale (ratio 1.25 from 16px; storefront):
`--text-sm` 14px · `--text-md` 16px · `--text-body` 18px (serif reading) · `--text-lead` 21px · `--text-title` 25px · `--text-section` clamp(2.25rem, 4vw, 3.25rem) · `--text-display-s` clamp(2.75rem, 5vw, 3.75rem) · `--text-display` clamp(3.25rem, 7vw, 5.25rem).
Admin screens use the app scale (ratio 1.2, no fluid heads): 13 · 14 · 16 · 19 · 23 · 28px.

Never: a serif heading, Bricolage at default width for headings, all-caps labels, tracked caps, italic words inside headings, more than these two families.

## 4. Space, layout, shape

- **Spacing scale:** `--space-3xs` 2 · `2xs` 4 · `xs` 8 · `sm` 12 · `md` 16 · `lg` 24 · `xl` 40 · `2xl` 64 · `3xl` 96 · `4xl` 144 (px). Raw lengths only via tokens.
- **Container:** max 1440px, content 1312px, gutter 64px desktop → 24px tablet → 16px phone; 12 columns, 32px gap (16px on phones). Grows gutters, not grids, past 1440.
- **Radius:** 0 everywhere (buttons, inputs, cards, images, badges, modals). Bootstrap's `--bs-border-radius*` are all set to 0.
- **Rules instead of boxes:** a 4px ink rule opens a section or table; 1px `--color-rule` hairlines separate rows and product cards. Product cards are **not** boxed: image on `paper-3`, then text, separated from neighbours by grid gap and hairlines.
- **Depth:** a paper step (`paper-2` well) — never a raised card. One permitted shadow, for floating layers only (dropdown, mega menu, quick-view card, toast): `--shadow-pop: 0 1px 2px oklch(20% 0.01 280 / 0.08), 0 8px 24px oklch(20% 0.01 280 / 0.10)` together with a 1px ink border.
- **Z-index:** base 1, raised 10, dropdown 100, sticky 200, sticky-nav 300, modal 400, toast 500, tooltip 600.
- **Product images:** square (1:1) on `paper-3`, `object-fit: contain` with 8% inner padding so products of every shape line up; a 1px ink outline at 8% opacity.

## 5. Controls

- **Primary button:** ink fill, paper text, 48px tall (40px in admin), square, label face 500. Hover: one step lighter ink (`--color-ink-2`). Pressed: translateY(1px). Disabled: opacity 0.55 + `cursor: not-allowed`.
- **Secondary button:** 1px ink outline, transparent fill. **Text button:** hairline underline that turns green on hover.
- **Destructive:** outlined in `--color-danger`, verb label ("Remove item", "Cancel order", "Delete product"), always confirmed.
- **Inputs/selects:** 52px (store) / 40px (admin), 1px `--color-rule-2` border, square; focus → 2px green outline inset; error → danger border + message below in danger with an icon; helper text in muted.
- **Quantity stepper:** − / number / + in one ruled strip, 44px hit targets, bounded by stock.
- **Chips (filters):** label face, 1px rule border; active = green outline + green text + "×" to remove.
- **Badges:** square, label face 13px, status colour on wash.
- **Every interactive element** has eight states considered (default, hover, focus-visible, active, disabled, loading, error, success where relevant). Focus is instant, never animated.

## 6. Icons

**Bootstrap Icons 1.13.2** (MIT), self-hosted font + CSS, `1.25em`, `currentColor`, always paired with a text label or `aria-label`. Used sparingly: search, cart, user, heart-free (no wishlist), truck (delivery), shield-check (payment), star/star-fill/star-half, chevrons, x, check, chat. No icon tiles, no emoji.

## 7. Motion principles

**Posture: tasteful, purposeful motion.** The Editorial theme's default is "state only"; the owner widened it for this project (see DECISIONS.md). Motion is welcome wherever it helps someone shop: it confirms an action, shows a change of state, guides the eye, or makes loading feel shorter. It never decorates for its own sake.

Tokens: durations `--dur-micro` 120ms, `--dur-short` 220ms, `--dur-long` 420ms, `--dur-reveal` 600ms; easings `--ease-out: cubic-bezier(0.2, 0.7, 0.2, 1)`, `--ease-in: cubic-bezier(0.4, 0, 1, 1)`, `--ease-in-out: cubic-bezier(0.6, 0, 0.4, 1)`. Animate only `transform` and `opacity` (plus `color`/`background-color`/`border-color` on micro state changes). Never `transition: all`. Exits run at ~70% of the enter duration.

Where motion is used:
1. **Product cards (everywhere):** on hover/focus the image scales to 1.04 inside its frame (220ms), the hairline under the card darkens to ink, and a quiet "Quick view" / "Add to cart" row slides up 6px into view. Touch devices show the row at rest.
2. **Sponsored / featured strip (homepage):** smooth continuous drift (~40px/s) driven by GSAP; pauses on hover, focus-within and while a quick view is open; visible pause/play and prev/next buttons (prev/next glide 420ms); stops when off-screen.
3. **Quick-view card:** fades in and rises 8px (220ms) after a 150ms hover-intent delay, or at once on focus/tap; closes with Esc, blur or the close button.
4. **Add to cart:** button goes "Adding…" (spinner) → "Added" with a check for 1.5s, then back; the cart badge bumps once (scale 1 → 1.25 → 1, 360ms) and its count rolls to the new number.
5. **Toasts:** slide in 12px from the bottom-right with a fade (220ms), auto-dismiss after 4s (paused on hover/focus), slide out on close.
6. **Skeleton loaders:** recommendation blocks, similar products and the AI Explainer data show skeletons in the shape of the content with a slow 1.6s shimmer; content cross-fades in (220ms).
7. **Scroll reveals:** sections and product grids settle in once (fade + 12px rise, 600ms, 40ms stagger between cards) via ScrollTrigger `batch`. Content is visible without JavaScript; reveals run only on the storefront, never on forms or admin tables.
8. **Navigation:** the mega menu and dropdowns fade/drop 6px (220ms); the mobile offcanvas slides; the header gains a hairline shadow once the page scrolls.
9. **Forms & cart:** quantity changes update line and order totals with a short number tween; removed cart rows collapse (opacity + translate, then height via a class swap); inline errors fade in.
10. **AI Explainer:** step transitions (slide + fade 420ms); TF-IDF weight bars grow from 0 with `scaleX` and a 40ms stagger; similarity rows re-order with GSAP Flip; Next/Back/Play/Pause controls.
11. **Checkout progress:** the step indicator fills to the current step; payment result pages draw their check/cross icon once.
12. ~~**Lenis smooth scrolling**~~ **not used (Phase 9):** it fought the sticky-header and tab-bar scroll padding, keyboard focus scrolling and hash links; native scrolling is kept (DECISIONS, Design pass). The vendored file stays in `static/vendor/` unused.

Admin screens: state motion only (hover, focus, toasts, dropdowns, skeletons). No reveals on admin tables.

Never: parallax, cursor followers, bouncing/elastic easing, glow, spinning or pulsing decoration, auto-rotating hero carousels, motion longer than 600ms on UI state, animation that blocks input.

**`prefers-reduced-motion: reduce`:** every reveal shows its end state at once, the sponsored strip stops (it becomes a manually scrollable rail with the same buttons), Lenis is not started, skeleton shimmer stops (static block), badge bumps and number tweens become instant swaps; colour/opacity feedback of 120ms or less stays.

## 8. Bootstrap mapping

Bootstrap 5.3 supplies the grid, utilities, collapse, dropdown, modal, offcanvas and toast JS. Its look is overridden in `static/css/bootstrap-overrides.css` by mapping `--bs-*` variables to the tokens: body font/colour/bg, `--bs-border-radius*: 0`, `--bs-link-color` ink, `--bs-primary` ink, `--bs-success` accent, `--bs-danger` danger, focus ring green, `.btn`, `.form-control`, `.table`, `.badge`, `.dropdown-menu`, `.modal-content`, `.toast` restyled. No stock Bootstrap blue anywhere.

## 9. Responsive

Breakpoints follow Bootstrap (576 / 768 / 992 / 1200 / 1400). Under 992px: mega menu becomes an offcanvas category list, filter column becomes a bottom-sheet offcanvas with chips on top, the product buy box becomes a sticky bottom bar. Under 768px: bottom tab bar (Home, Categories, Search, Cart, Account), 2-column product grid, tables restack as labelled blocks. Touch targets ≥ 44px. `overflow-x: clip` on html and body.

## 10. Accessibility

WCAG 2.2 AA: text contrast ≥ 4.5:1 (values above), UI ≥ 3:1, visible focus, labels on every field, `aria-live` for cart count and toasts, skip link, landmarks, alt text on product images ("{product_name} by {brand}"), keyboard-operable carousel and quick view, reduced-motion support.
