"""Print the store's fictional brand names onto plain product packaging in the photos.

Some product photos show blank tubes, bottles or devices. This script adds a label in the
product's own (invented) brand and name so the photo matches its listing. The unedited photo
is kept in media/products/originals/<slug>.jpg and every run starts from that original, so the
script is safe to run again. Ink is blended with the photo's own shading so it reads as print.

Run from the project root:  .venv\\Scripts\\python.exe scripts\\brand_labels.py
Every result must be checked by eye afterwards.
"""

import shutil
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
PRODUCTS = ROOT / "media" / "products"
ORIGINALS = PRODUCTS / "originals"
DISPLAY = ROOT / "static" / "fonts" / "bricolage-grotesque-latin-standard-normal.woff2"
SERIF = ROOT / "static" / "fonts" / "source-serif-4-latin-opsz-normal.woff2"
SERIF_ITALIC = ROOT / "static" / "fonts" / "source-serif-4-latin-opsz-italic.woff2"


def font(kind: str, size: int, weight: int = 700, width: int = 100) -> ImageFont.FreeTypeFont:
    """Load one of the store's variable fonts at a given weight (and width for Bricolage)."""
    if kind == "display":
        f = ImageFont.truetype(str(DISPLAY), size)
        f.set_variation_by_axes([min(max(size, 12), 96), weight, width])  # opsz, wght, wdth
    else:
        f = ImageFont.truetype(str(SERIF_ITALIC if kind == "italic" else SERIF), size)
        axes = f.get_variation_axes()
        values = []
        for axis in axes:
            name = axis["name"].decode() if isinstance(axis["name"], bytes) else axis["name"]
            values.append(min(max(size, axis["minimum"]), axis["maximum"]) if "ptical" in name else weight)
        f.set_variation_by_axes(values)
    return f


def draw_line(layer: Image.Image, text: str, fnt, centre: tuple[int, int], colour, tracking: float = 0.0) -> None:
    """Draw one centred line of text with optional letter spacing (in em)."""
    draw = ImageDraw.Draw(layer)
    extra = tracking * fnt.size
    widths = [draw.textlength(ch, font=fnt) for ch in text]
    total = sum(widths) + extra * (len(text) - 1)
    x = centre[0] - total / 2
    for ch, w in zip(text, widths):
        draw.text((x, centre[1]), ch, font=fnt, fill=colour, anchor="lm")
        x += w + extra


def apply_label(base: Image.Image, spec: dict) -> Image.Image:
    """Render the spec's lines on a transparent layer, rotate/blur it, and blend into the photo."""
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    for line in spec["lines"]:
        text, kind, size, weight, dy = line[:5]
        opts = line[5] if len(line) > 5 else {}
        fnt = font(kind, size, weight, opts.get("width", 100))
        colour = opts.get("colour", spec["ink"])
        draw_line(layer, text, fnt, (spec["at"][0], spec["at"][1] + dy), colour, opts.get("tracking", 0.0))
    if spec.get("angle"):
        layer = layer.rotate(spec["angle"], resample=Image.Resampling.BICUBIC, center=spec["at"])
    layer = layer.filter(ImageFilter.GaussianBlur(spec.get("blur", 0.45)))

    photo = np.asarray(base, dtype=np.float32) / 255.0
    paint = np.asarray(layer, dtype=np.float32) / 255.0
    rgb, alpha = paint[..., :3], paint[..., 3:4] * spec.get("opacity", 0.92)
    if spec.get("mode", "multiply") == "multiply":  # dark ink on a light surface
        out = photo * (1 - alpha) + photo * rgb * alpha
    else:  # light ink on a dark surface: follow the surface's own light and shade
        shade = 0.55 + 0.9 * photo.mean(axis=2, keepdims=True)
        out = photo * (1 - alpha) + np.clip(rgb * shade, 0, 1) * alpha
    return Image.fromarray(np.clip(out * 255 + 0.5, 0, 255).astype(np.uint8))


# slug -> label spec. "at" = centre of the label (900 px image), dy = line offset from that centre.
LABELS = {
    "neem-ash-neem-and-tea-tree-face-wash": {
        "at": (452, 420), "ink": (38, 78, 52), "lines": [
            ("NEEM & ASH", "display", 30, 760, -70, {"tracking": 0.14, "width": 100}),
            ("Neem and", "serif", 40, 600, -10),
            ("Tea Tree", "serif", 40, 600, 34),
            ("face wash", "italic", 30, 400, 86, {"colour": (70, 100, 78)}),
            ("for oily, acne-prone skin  ·  100 ml", "display", 14, 450, 136, {"colour": (90, 110, 96)}),
        ]},
    "dewlab-spf-50-sunscreen-gel": {
        "at": (432, 400), "ink": (32, 30, 40), "lines": [
            ("dewlab", "display", 46, 780, -86, {"width": 100}),
            ("SPF 50", "display", 64, 800, -12, {"width": 75, "colour": (214, 104, 74)}),
            ("PA++++", "display", 22, 600, 40, {"tracking": 0.12, "colour": (214, 104, 74)}),
            ("Sunscreen gel", "serif", 26, 500, 88),
            ("broad spectrum  ·  no white cast  ·  50 g", "display", 13, 450, 128, {"colour": (95, 90, 100)}),
        ]},
    "dewlab-10-vitamin-c-face-serum": {
        "at": (460, 565), "ink": (45, 35, 30), "blur": 0.6, "lines": [
            ("dewlab", "display", 30, 780, -48),
            ("Vitamin C 10%", "display", 19, 650, -8, {"colour": (176, 92, 40)}),
            ("face serum", "italic", 18, 400, 22),
            ("30 ml", "display", 12, 500, 52, {"colour": (90, 80, 70)}),
        ]},
    "mitti-naturals-sulphate-free-shampoo": {
        "at": (418, 500), "ink": (250, 250, 244), "mode": "light", "blur": 1.4, "opacity": 0.97, "lines": [
            ("MITTI", "display", 92, 800, -96, {"tracking": 0.06, "width": 80}),
            ("NATURALS", "display", 34, 700, -26, {"tracking": 0.3}),
            ("sulphate-free", "serif", 42, 600, 44),
            ("shampoo", "serif", 42, 600, 92),
            ("250 ml", "display", 20, 600, 150, {"tracking": 0.1}),
        ]},
    "mitti-naturals-onion-hair-oil": {
        "at": (490, 470), "ink": (96, 40, 14), "angle": 21, "opacity": 0.86, "lines": [
            ("MITTI NATURALS", "display", 20, 700, -58, {"tracking": 0.2}),
            ("Onion", "serif", 50, 700, -8),
            ("hair oil", "italic", 32, 400, 40),
            ("with coconut  ·  200 ml", "display", 14, 500, 80),
        ]},
    "kesari-botanicals-kumkumadi-face-oil": {
        "at": (600, 610), "ink": (104, 24, 20), "blur": 0.6, "opacity": 0.9, "lines": [
            ("KESARI", "display", 28, 800, -36, {"tracking": 0.22}),
            ("Kumkumadi", "serif", 32, 600, 4),
            ("face oil  ·  15 ml", "display", 14, 500, 38),
        ]},
    "ferrow-snap-24-mirrorless-camera": {
        "at": (548, 268), "ink": (214, 214, 210), "mode": "light", "blur": 0.5, "opacity": 0.88, "lines": [
            ("FERROW", "display", 24, 700, 0, {"tracking": 0.28, "width": 100}),
        ]},
    "steelwell-ro-uv-water-purifier": {
        "at": (262, 560), "ink": (40, 46, 60), "blur": 0.55, "lines": [
            ("steelwell", "display", 36, 760, -18),
            ("RO + UV purifier", "display", 15, 500, 18, {"tracking": 0.06, "colour": (90, 96, 110)}),
        ]},
    "hearthline-indoor-security-camera-2k": {
        "at": (446, 700), "ink": (92, 92, 96), "blur": 0.6, "lines": [
            ("hearthline", "display", 22, 650, 0, {"tracking": 0.04}),
        ]},
    "groomwell-cordless-beard-trimmer": {
        "at": (432, 650), "ink": (200, 178, 156), "mode": "light", "angle": 90, "blur": 0.5, "opacity": 0.85, "lines": [
            ("GROOMWELL", "display", 20, 700, 0, {"tracking": 0.26}),
        ]},
    "lumora-55-inch-qled-smart-tv": {
        "at": (450, 0), "ink": (170, 170, 176), "mode": "light", "blur": 0.4, "opacity": 0.9, "lines": [
            ("LUMORA", "display", 11, 700, 0, {"tracking": 0.3}),
        ]},
}


def tv_bezel_y(image: Image.Image, x: int = 450) -> int:
    """Find the middle of the TV's bottom bezel (the darkest short run of rows below the screen)."""
    column = np.asarray(image.convert("L"), dtype=np.float32)[560:760, x - 60:x + 60].mean(axis=1)
    dark = np.where(column < 70)[0]
    if not len(dark):
        return 698
    runs, start = [], dark[0]
    for a, b in zip(dark, dark[1:]):
        if b != a + 1:
            runs.append((start, a)); start = b
    runs.append((start, dark[-1]))
    lo, hi = runs[-1]
    return 560 + (lo + hi) // 2


def main() -> None:
    ORIGINALS.mkdir(parents=True, exist_ok=True)
    for slug, spec in LABELS.items():
        target = PRODUCTS / f"{slug}.jpg"
        original = ORIGINALS / f"{slug}.jpg"
        if not original.exists():
            if not target.exists():
                print(f"missing photo: {slug}")
                continue
            shutil.copy2(target, original)
        base = Image.open(original).convert("RGB")
        if slug.startswith("lumora"):
            spec = {**spec, "at": (450, tv_bezel_y(base))}
        apply_label(base, spec).save(target, "JPEG", quality=86, optimize=True, progressive=True)
        print(f"labelled {slug}")


if __name__ == "__main__":
    main()
