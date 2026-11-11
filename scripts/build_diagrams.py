r"""Build the three docs diagrams in docs/diagrams/ (architecture, recommender data flow, checkout sequence).

Follows the Diagram Design skill conventions with Velora's colour tokens and system fonts (works offline).
Run (PowerShell): .venv\Scripts\python.exe scripts\build_diagrams.py   (PNG copies for the README: the skills export_png.py)
"""
from pathlib import Path
from html import escape

OUT = Path(__file__).resolve().parent.parent / "docs" / "diagrams"
OUT.mkdir(parents=True, exist_ok=True)

# Velora tokens (docs/DESIGN_SYSTEM.md, converted from OKLCH)
PAPER, PAPER2, INK, MUTED, RULE, ACCENT, LINK = "#f7f5f0", "#eeebe4", "#0c0d12", "#615d57", "#d0cdc7", "#007439", "#385b7e"
ACCENT_TINT = "rgba(0,116,57,0.08)"
SANS = "'Bricolage Grotesque', system-ui, sans-serif"
SERIF = "'Source Serif 4', Georgia, serif"
MONO = "'Cascadia Mono', Consolas, ui-monospace, monospace"

TREAT = {  # node treatments from the style guide
    "focal": (ACCENT_TINT, ACCENT, ""), "backend": ("#ffffff", INK, ""), "store": ("rgba(12,13,18,0.05)", MUTED, ""),
    "input": ("rgba(97,93,87,0.10)", MUTED, ""), "external": ("rgba(12,13,18,0.03)", "rgba(12,13,18,0.30)", ""),
}


def node(x, y, w, h, tag, name, subs, kind="backend"):
    fill, stroke, dash = TREAT[kind]
    tag_w = len(tag) * 6 + 12
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{PAPER}"/>',
           f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{fill}" stroke="{stroke}" stroke-width="1"/>',
           f'<rect x="{x + 12}" y="{y + 10}" width="{tag_w}" height="13" rx="2" fill="none" stroke="{stroke}" stroke-width="0.8"/>',
           f'<text x="{x + 12 + tag_w / 2}" y="{y + 19.5}" fill="{ACCENT if kind == "focal" else MUTED}" font-size="7" font-family="{MONO}" '
           f'text-anchor="middle" letter-spacing="0.14em">{escape(tag)}</text>',
           f'<text x="{x + 12}" y="{y + 40}" fill="{INK}" font-size="12.5" font-weight="600" font-family="{SANS}">{escape(name)}</text>']
    for i, s in enumerate(subs):
        out.append(f'<text x="{x + 12}" y="{y + 55 + i * 12}" fill="{MUTED}" font-size="9" font-family="{MONO}">{escape(s)}</text>')
    return "\n".join(out)


def path(d, kind="muted", dashed=False):
    color = {"muted": MUTED, "accent": ACCENT, "link": LINK}[kind]
    marker = {"muted": "arrow", "accent": "arrow-accent", "link": "arrow-link"}[kind]
    dash = ' stroke-dasharray="4,3"' if dashed else ""
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{1 if dashed else 1.2}"{dash} marker-end="url(#{marker})"/>'


def label(cx, cy, text, color=MUTED):
    w = len(text) * 5.4 + 8
    return (f'<rect x="{cx - w / 2:.1f}" y="{cy - 7}" width="{w:.1f}" height="12" rx="2" fill="{PAPER}"/>'
            f'<text x="{cx}" y="{cy + 2}" fill="{color}" font-size="8" font-family="{MONO}" text-anchor="middle" letter-spacing="0.06em">{escape(text)}</text>')


def zone(x, y, w, h, text):
    lw = len(text) * 6 + 16
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="rgba(12,13,18,0.02)" stroke="rgba(12,13,18,0.14)" stroke-width="0.8"/>'
            f'<rect x="{x + 12}" y="{y + 4}" width="{lw}" height="12" rx="2" fill="{PAPER}"/>'
            f'<text x="{x + 12 + lw / 2}" y="{y + 13}" fill="{MUTED}" font-size="7" font-family="{MONO}" text-anchor="middle" letter-spacing="0.14em">{escape(text)}</text>')


def legend(y, width, items):
    out = [f'<line x1="30" y1="{y - 8}" x2="{width - 30}" y2="{y - 8}" stroke="rgba(12,13,18,0.12)" stroke-width="0.8"/>',
           f'<text x="30" y="{y + 12}" fill="{MUTED}" font-size="8" font-family="{MONO}" letter-spacing="0.14em">LEGEND</text>']
    x = 110
    for kind, text in items:
        if kind.startswith("line"):
            dashed = kind == "line-dashed"
            color = ACCENT if kind == "line-accent" else MUTED
            out.append(f'<line x1="{x}" y1="{y + 9}" x2="{x + 24}" y2="{y + 9}" stroke="{color}" stroke-width="1.2"{" stroke-dasharray=\"4,3\"" if dashed else ""}/>')
        else:
            fill, stroke, _ = TREAT[kind]
            out.append(f'<rect x="{x}" y="{y + 3}" width="24" height="12" rx="3" fill="{fill}" stroke="{stroke}" stroke-width="1"/>')
        out.append(f'<text x="{x + 32}" y="{y + 12}" fill="{INK}" font-size="9.5" font-family="{SANS}">{escape(text)}</text>')
        x += 32 + len(text) * 5.6 + 28
    return "\n".join(out)


def page(slug, eyebrow, title, desc, caption, width, height, body):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{escape(title)} · Velora</title>
  <style>
    /* System font mode (Diagram Design): no network, no external files; Velora's faces are used when installed. */
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    :root {{ --paper: {PAPER}; --ink: {INK}; --muted: {MUTED}; }}
    body {{ font-family: {SANS}; background: var(--paper); color: var(--ink); min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 3rem 2rem; }}
    .frame {{ max-width: 1200px; width: 100%; }}
    .diagram-container {{ width: 100%; overflow-x: auto; }}
    .eyebrow {{ font-family: {MONO}; font-size: 0.66rem; letter-spacing: 0.18em; text-transform: uppercase; color: var(--muted); margin-bottom: 0.5rem; }}
    h1 {{ font-family: {SERIF}; font-size: clamp(1.5rem, 2.4vw + 0.75rem, 2rem); font-weight: 400; letter-spacing: -0.01em; line-height: 1.15; margin-bottom: 1.5rem; }}
    .caption {{ font-family: {SERIF}; font-style: italic; color: var(--muted); max-width: 70ch; margin-top: 1rem; line-height: 1.5; }}
    svg {{ width: 100%; min-width: {width}px; display: block; }}
    @media print {{ .diagram-container {{ overflow-x: visible; }} svg {{ min-width: 0; }} }}
  </style>
</head>
<body>
  <div class="frame">
    <p class="eyebrow">{escape(eyebrow)} · Velora docs</p>
    <h1>{escape(title)}</h1>
    <div class="diagram-container">
      <svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="{slug}-title {slug}-desc">
        <title id="{slug}-title">{escape(title)}</title>
        <desc id="{slug}-desc">{escape(desc)}</desc>
        <defs>
          <marker id="arrow" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{MUTED}"/></marker>
          <marker id="arrow-accent" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{ACCENT}"/></marker>
          <marker id="arrow-link" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{LINK}"/></marker>
          <marker id="arrow-open" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polyline points="0 0, 8 3, 0 6" fill="none" stroke="{MUTED}" stroke-width="1.2"/></marker>
        </defs>
        <rect width="100%" height="100%" fill="{PAPER}"/>
{body}
      </svg>
    </div>
    <p class="caption">{escape(caption)}</p>
  </div>
</body>
</html>
"""


# ------------------------------------------------------------------ 1. architecture
W, H = 192, 72
b = [zone(224, 104, 464, 280, "DJANGO PROJECT"), zone(224, 416, 464, 120, "TEST HARNESS"), zone(720, 104, 224, 432, "SQLITE FILES")]
b += [
    path("M192,240 H208 Q216,240 216,232 V180 Q216,172 224,172 H240", "link"),
    path("M192,264 H208 Q216,264 216,272 V324 Q216,332 224,332 H240", "link"),
    path("M432,172 H480", "muted"),
    path("M400,296 V260 Q400,252 408,252 H504 Q512,252 512,244 V208", "muted"),
    path("M600,208 V296", "accent"), label(652, 252, "SIMILAR, PICKS", ACCENT),
    path("M672,172 H736", "muted"), label(704, 160, "ORM"),
    path("M672,332 H784 Q792,332 792,324 V208", "muted"), label(744, 320, "READS"),
    path("M336,448 V368", "muted", dashed=True), label(380, 408, "LIVE SERVER"),
    path("M432,484 H480", "muted"),
    path("M672,484 H736", "muted"), label(704, 472, "WRITES"),
]
b += [
    node(32, 216, 160, H, "INPUT", "Browser", ["customer or admin"], "input"),
    node(240, 136, W, H, "APPS", "Storefront apps", ["catalog, orders, reviews,", "messaging, accounts, core"]),
    node(240, 296, W, H, "APP", "Admin panel", ["adminpanel/ (staff only)"]),
    node(480, 136, W, H, "SERVICES", "Service layer", ["cart, checkout, payment,", "status, catalog, messaging"], "focal"),
    node(480, 296, W, H, "AI", "Recommender", ["recommender/engine.py", "TF-IDF + cosine"], "focal"),
    node(736, 136, W, H, "STORE", "db.sqlite3", ["shop data: products,", "orders, customers, ..."], "store"),
    node(240, 448, W, H, "TESTS", "Pytest + Playwright", ["185 tests, live_server,", "test_db.sqlite3"]),
    node(480, 448, W, H, "COMMAND", "record_test_run", ["results.json per run"]),
    node(736, 448, W, H, "STORE", "reports.sqlite3", ["TestCase, TestSummary,", "TestExecution"], "store"),
    legend(576, 960, [("focal", "Focal: business logic + AI"), ("backend", "Component"), ("store", "Data store"),
                      ("input", "Browser"), ("line-dashed", "Test time only")]),
]
(OUT / "architecture.html").write_text(page(
    "architecture", "Architecture", "How Velora fits together",
    "The browser talks to Django apps, which call a service layer and the recommender; shop data and test results live in two separate SQLite files.",
    "Views stay thin: business rules live in the service layer (orders/services, catalog/services, messaging/services, reviews/services) and the recommender. "
    "Shop data and test results are separate SQLite files, so a test run can never touch shop data. The admin's Test Reports page reads reports.sqlite3.",
    960, 640, "\n".join(b)), encoding="utf-8")

# ------------------------------------------------------------------ 2. recommender data flow
W2, H2 = 176, 72
b = [zone(24, 96, 832, 112, "BUILT ONCE, CACHED UNTIL PRODUCTS CHANGE")]
b += [
    path("M216,152 H248", "muted"),
    path("M424,152 H456", "muted"),
    path("M632,152 H664", "accent"),
    path("M752,192 V280", "muted"),
    path("M704,192 V224 Q704,232 696,232 H552 Q544,232 544,240 V280", "muted"),
    path("M424,316 H456", "muted"),
    path("M544,352 V416", "muted", dashed=True), label(592, 384, "NO HISTORY"),
    path("M424,452 H456", "muted"),
]
b += [
    node(40, 120, W2, H2, "STORE", "ProductFeature", ["category, name, brand,", "description, keywords"], "store"),
    node(248, 120, W2, H2, "PANDAS", "Clean + combine", ["name x3, keywords x3,", "category x2, brand, desc"]),
    node(456, 120, W2, H2, "SCIKIT-LEARN", "TF-IDF vectors", ["words + 2-word phrases,", "min_df=2"]),
    node(664, 120, W2, H2, "CACHE", "Cosine similarity", ["product x product matrix", "get_engine()"], "focal"),
    node(248, 280, W2, H2, "STORE", "Interactions", ["view 1, cart 2, buy 3,", "halves every 14 days"], "store"),
    node(456, 280, W2, H2, "OUTPUT", "Recommended for you", ["weighted average of", "similarity to interests"], "focal"),
    node(664, 280, W2, H2, "OUTPUT", "Similar products", ["top 6, never itself"]),
    node(248, 416, W2, H2, "STORE", "Orders + ratings", ["most ordered, best rated"], "store"),
    node(456, 416, W2, H2, "OUTPUT", "Popular picks", ["new customers"]),
    legend(536, 880, [("focal", "Focal"), ("backend", "Step / output"), ("store", "Data read"), ("line-dashed", "Fallback")]),
]
(OUT / "recommender.html").write_text(page(
    "recommender", "Data flow", "How a recommendation is made",
    "Product text is cleaned, weighted and turned into TF-IDF vectors; cosine similarity between them drives similar products, personal picks and a popular fallback.",
    "Only active, in-stock products are ever suggested: stock and status are read live on every call, so a product that sells out drops out at once. "
    "The AI Explainer page (/ai/explainer/) shows each of these steps for any product.",
    880, 600, "\n".join(b)), encoding="utf-8")

# ------------------------------------------------------------------ 3. checkout sequence
LX = {"cust": 96, "views": 296, "chk": 496, "pay": 696, "db": 896}
names = [("cust", "INPUT", "Customer", ["browser"], "input"), ("views", "VIEWS", "orders/views.py", ["checkout, payment"], "backend"),
         ("chk", "SERVICE", "submit_cart()", ["services/checkout.py"], "focal"), ("pay", "SERVICE", "pay()", ["services/payment.py"], "backend"),
         ("db", "STORE", "db.sqlite3", ["one transaction"], "store")]
top, bottom = 40 + 72, 708
b = [f'<line x1="{x}" y1="{top}" x2="{x}" y2="{bottom}" stroke="rgba(12,13,18,0.25)" stroke-width="1" stroke-dasharray="3,4"/>' for x in LX.values()]


def msg(y, a, z, text, kind="muted", dashed=False, open_head=False):
    x1, x2 = LX[a], LX[z]
    d = 1 if x2 > x1 else -1
    out = [path(f"M{x1 + 4 * d},{y} H{x2 - 4 * d}", kind, dashed)]
    if open_head:
        out[0] = out[0].replace("url(#arrow)", "url(#arrow-open)")
    out.append(label((x1 + x2) / 2, y - 12, text, ACCENT if kind == "accent" else MUTED))
    return "\n".join(out)


# alt frame (payment outcome)
b += [f'<rect x="64" y="392" width="860" height="300" rx="4" fill="rgba(12,13,18,0.02)" stroke="rgba(12,13,18,0.22)" stroke-width="1"/>',
      f'<rect x="64" y="392" width="40" height="16" rx="2" fill="{PAPER}" stroke="rgba(12,13,18,0.22)" stroke-width="1"/>',
      f'<text x="84" y="404" fill="{MUTED}" font-size="8" font-family="{MONO}" text-anchor="middle" letter-spacing="0.12em">ALT</text>',
      f'<text x="112" y="404" fill="{MUTED}" font-size="8" font-family="{MONO}">[payment succeeds]</text>',
      f'<line x1="72" y1="592" x2="916" y2="592" stroke="rgba(12,13,18,0.20)" stroke-width="1" stroke-dasharray="4,3"/>',
      f'<text x="76" y="608" fill="{MUTED}" font-size="8" font-family="{MONO}">[payment fails]</text>']
b += [
    msg(152, "cust", "views", "PLACE ORDER + KEY", "link"),
    msg(192, "views", "chk", "SUBMIT_CART()"),
    msg(232, "chk", "db", "LOCK, CHECK STOCK, DECREMENT, ADD ROWS"),
    msg(272, "db", "chk", "ORDER_ID (PENDING)", dashed=True),
    msg(312, "views", "cust", "REDIRECT TO PAYMENT", dashed=True),
    msg(352, "cust", "views", "PAY: METHOD + OUTCOME", "link"),
    msg(436, "views", "pay", "PAY()"),
    msg(476, "pay", "db", "PAYMENT OK, CONFIRMED, CLEAR CART"),
    msg(516, "views", "cust", "CONFIRMATION PAGE", "accent", dashed=True),
    msg(564, "pay", "cust", "ORDER EMAIL (ON COMMIT)", dashed=True, open_head=True),
    msg(636, "pay", "db", "PAYMENT FAILED, ORDER PENDING"),
    msg(676, "views", "cust", "TRY AGAIN", dashed=True),
]
for key, tag, name, subs, kind in names:
    b.append(node(LX[key] - 88, 40, 176, 72, tag, name, subs, kind))
b.append(legend(744, 1000, [("line-accent", "Headline success"), ("line", "Call"), ("line-dashed", "Return / async"), ("focal", "Focal step")]))
(OUT / "checkout.html").write_text(page(
    "checkout", "Sequence", "Checkout and dummy payment",
    "Placing an order reserves stock and creates pending order rows in one transaction; a simulated payment then confirms the order or leaves it pending for a retry.",
    "The checkout key stops a double click from creating a second order. Cart lines are cleared only after a successful payment, and the order email "
    "is sent only once that transaction has committed. An admin cancelling an order puts the stock back.",
    1000, 800, "\n".join(b)), encoding="utf-8")
print("written:", [p.name for p in OUT.iterdir()])
