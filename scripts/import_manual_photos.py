"""Copy hand-picked product photos from media/manual_photos/ into the catalogue.

Each photo is centre-cropped to a square and resized to 900 px JPEG, exactly like the
other product images, and saved as media/products/<product-slug>.jpg.
Run from the project root:  .venv\\Scripts\\python.exe scripts\\import_manual_photos.py
Then run `python manage.py seed_demo` so the products point at the new files.
"""

from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "media" / "manual_photos"
TARGET = ROOT / "media" / "products"

# file in media/manual_photos  ->  (product slug, horizontal crop centre 0..1)
PHOTOS = {
    "Dewy White Skincare Tube with Green Leaves.png": ("neem-ash-neem-and-tea-tree-face-wash", 0.5),
    "Minimalist Coral-Capped Lotion Tube.png": ("dewlab-spf-50-sunscreen-gel", 0.5),
    "Matte Black Mirrorless Camera.png": ("ferrow-snap-24-mirrorless-camera", 0.5),
    "Modern TV with Gradient Wave Display.png": ("lumora-55-inch-qled-smart-tv", 0.5),
    "Modern Wall-Mounted Water Purifier.png": ("steelwell-ro-uv-water-purifier", 0.5),
    "Modern White Security Camera on Wooden Shelf.png": ("hearthline-indoor-security-camera-2k", 0.5),
    "Polished Wooden Ludo Board and Dice.png": ("gameshala-ludo-and-snakes-and-ladders-2-in-1", 0.5),
    "Sleek Charcoal Beard Trimmer Set.png": ("groomwell-cordless-beard-trimmer", 0.5),
    "Sleek Smartphone with Screen Protector.png": ("shieldguard-tempered-glass-screen-protector-for-nova", 0.5),
    "pexels-kindelmedia-9029794.jpg": ("tinkerbox-solar-robot-science-kit", 0.5),
    "Minimalist Black Soundbar and Subwoofer.png": ("sonvale-soundbar-21-with-subwoofer", 0.5),
    # A smartwatch, so it goes on the Orvia smartwatch listing (the Thread & Thali watch is analog).
    "Modern Smartwatch with Gradient Wave Dial.png": ("orvia-fit-smartwatch-with-calling", 0.5),
    "Modern Stainless Steel Microwave Oven.png": ("tadka-home-solo-microwave-oven-20-l", 0.5),
}


def main() -> None:
    TARGET.mkdir(parents=True, exist_ok=True)
    for filename, (slug, centre_x) in PHOTOS.items():
        source = SOURCE / filename
        if not source.exists():
            print(f"missing: {filename}")
            continue
        image = ImageOps.exif_transpose(Image.open(source)).convert("RGB")
        image = ImageOps.fit(image, (900, 900), Image.Resampling.LANCZOS, centering=(centre_x, 0.5))
        image.save(TARGET / f"{slug}.jpg", "JPEG", quality=84, optimize=True, progressive=True)
        print(f"saved {slug}.jpg")


if __name__ == "__main__":
    main()
