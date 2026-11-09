# Manual product photos (from pexels.com)

Drop the downloaded photos here with these exact names, then tell Claude Code "photos added".
Any size or shape is fine: they will be cropped to a square, resized to 900 px and copied into `media/products/`,
and their credits (photographer + Pexels page URL) added to `docs/IMAGE_CREDITS.md`.
Put the photographer name and the Pexels page URL for each file in `credits.txt` (one line per file:
`file.jpg | Photographer Name | https://www.pexels.com/photo/...`).

Status (2026-11-09): 10 photos imported. Still wanted:

| File name | Product it replaces |
|---|---|
| soundbar.jpg | Sonvale Soundbar 2.1 with Subwoofer |
| watch.jpg | Thread & Thali Women's Minimalist Analog Watch |
| microwave.jpg | Tadka Home Solo Microwave Oven, 20 L |

Add each new file to the `PHOTOS` map in `scripts/import_manual_photos.py`, run it, then `python manage.py seed_demo`.

Pick photos without visible real brand logos.
