# Recommender check (Gate 8)

Run on 2026-11-09 against the demo catalogue (110 products, 10 categories) with `python manage.py build_recommender`:
623 shared TF-IDF terms, 110 × 110 similarity matrix, built in 0.06 s.

Settings: `TfidfVectorizer(stop_words="english", ngram_range=(1, 2), sublinear_tf=True, min_df=2)`, document =
name ×3 + keywords ×3 + category ×2 + brand + description. Only active, in-stock products are listed.

## Similar products (top 5)

### Arc 3 Wireless Earbuds (Electronics)
Top terms: wireless, noise, case, arc, wireless bluetooth

| Score | Product | Category | Shared terms |
|---|---|---|---|
| 0.493 | Field 700 Over-Ear Headphones | Electronics | noise, wireless, bluetooth |
| 0.376 | Pocket Bluetooth Speaker | Electronics | wireless, bluetooth, electronics |
| 0.294 | Soundbar 2.1 with Subwoofer | Electronics | arc, wireless, electronics |
| 0.169 | Silent Wireless Mouse | Computers and Laptops | wireless |
| 0.161 | Rugged Case for Nova | Mobile Phones and Accessories | case, pocket |

### Electric Kettle, 1.5 L (Kitchen and Home Appliances)
Top terms: tea, litre stainless, stainless, stainless steel, litre

| Score | Product | Category | Shared terms |
|---|---|---|---|
| 0.607 | Stainless Steel Pressure Cooker, 5 L | Kitchen and Home Appliances | stainless, steel, litre |
| 0.584 | Hand Blender, 400 W | Kitchen and Home Appliances | kitchen, appliance, stainless |
| 0.518 | Solo Microwave Oven, 20 L | Kitchen and Home Appliances | litre, kitchen, appliance |
| 0.437 | RO + UV Water Purifier | Kitchen and Home Appliances | kitchen, water, appliance |
| 0.375 | Drip Coffee Maker | Kitchen and Home Appliances | kitchen, appliance, appliances |

### Women's Block-Print Straight Kurta (Fashion and Clothing)
Top terms: kurta, block, straight, women, wear

| Score | Product | Category | Shared terms |
|---|---|---|---|
| 0.505 | Handloom Cotton Saree | Fashion and Clothing | women, ethnic, cotton |
| 0.431 | Men's Cotton-Silk Nehru Jacket | Fashion and Clothing | wear, ethnic, kurta |
| 0.294 | Women's High-Rise Wide-Leg Jeans | Fashion and Clothing | women, wear, jeans |
| 0.277 | Unisex Cotton Fleece Hoodie | Fashion and Clothing | wear, cotton, clothing |
| 0.246 | Men's Slim-Fit Oxford Shirt | Fashion and Clothing | wear, cotton, cut |

### Wooden Chess Set (Toys and Games)
Top terms: wooden, game, board, board game, game wooden

| Score | Product | Category | Shared terms |
|---|---|---|---|
| 0.630 | Full-Size Carrom Board | Toys and Games | board, game, wooden |
| 0.546 | Ludo and Snakes and Ladders, 2-in-1 | Toys and Games | game, board, games |
| 0.341 | 1000-Piece Jigsaw Puzzle, Spice Market | Toys and Games | board, pieces, games |
| 0.183 | City Fire Station Building Set, 720 Pieces | Toys and Games | set, pieces, games |
| 0.174 | Soft Teddy Bear, 40 cm | Toys and Games | cm, games, toys |

### Neem and Tea Tree Face Wash (Beauty and Personal Care)
Top terms: neem, tea, wash, face, oily

| Score | Product | Category | Shared terms |
|---|---|---|---|
| 0.460 | Hyaluronic Gel Moisturiser | Beauty and Personal Care | face, skin, skincare |
| 0.433 | Activated Charcoal Soap, Pack of 4 | Beauty and Personal Care | neem, care, skin |
| 0.411 | Kumkumadi Face Oil | Beauty and Personal Care | face, skincare, oil |
| 0.389 | SPF 50 Sunscreen Gel | Beauty and Personal Care | skincare, oily, gel |
| 0.385 | 10% Vitamin C Face Serum | Beauty and Personal Care | face, skincare, skin |

### Nova 5G Smartphone, 8 GB / 128 GB (Mobile Phones and Accessories)
Top terms: 5g, smartphone, gb, 5g phone, phone

| Score | Product | Category | Shared terms |
|---|---|---|---|
| 0.790 | Nova Pro 5G, 12 GB / 256 GB | Mobile Phones and Accessories | 5g, gb, phone |
| 0.750 | Lite 4G, 4 GB / 64 GB | Mobile Phones and Accessories | gb, phone, smartphone |
| 0.297 | Rugged Case for Nova | Mobile Phones and Accessories | phone, nova, mobile |
| 0.283 | Tempered Glass Screen Protector for Nova | Mobile Phones and Accessories | nova, phone, mobile |
| 0.227 | Air 14 Laptop, Ryzen 5, 16 GB, 512 GB SSD | Computers and Laptops | gb, ram, inch |

## Personalised (demo customers)

- **Asha Rao** (bought the action camera, headphones, Nova 5G phone and accessories; viewed a speaker and a smartwatch):
  Nova Pro 5G ("Because you bought Nova 5G Smartphone"), Bluetooth Selfie Stick Tripod and Magnetic Car Phone Mount
  ("Because you bought Trail Action Camera"), Lite 4G, Snap 24 Mirrorless Camera, Indoor Security Camera 2K,
  20000 mAh Power Bank, Soundbar. Products she already bought or has in her cart are never shown.
- **Imran Qureshi** (no activity): popular fallback, labelled "Popularity", led by Trail Action Camera (most ordered, score 1.00).

## Verdict

Sensible for every sample: the first two or three picks are always in the same category and share the obvious words.
The weak tail is explainable from the shared terms (earbuds → wireless mouse via "wireless"; phone → laptop via "gb").
Scores are cosine similarities, not percentages of certainty; a weighted average over several interests (personalised)
is naturally lower than a one-to-one similarity, which the Explainer page says in words.
