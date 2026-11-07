"""Demo catalogue for `manage.py seed_demo`.

Every brand here is invented. Product types are real. Prices are in rupees.
Each product: (product_name, brand, price, mrp or None, quantity, keywords, description, sponsored, image_query)
`image_query` is only used by `manage.py fetch_product_images` to find a licensed photo once.
"""

CATEGORIES = [
    ("Electronics", "Headphones, speakers, TVs, cameras, power banks and smart-home plugs and cameras."),
    ("Fashion and Clothing", "Everyday shirts and jeans, festive ethnic wear, jackets, bags and watches."),
    ("Home and Furniture", "Solid-wood furniture, sofas, bedding, curtains, rugs and lamps."),
    ("Books and Stationery", "Novels, cookbooks and how-to guides, plus pens, notebooks and art supplies."),
    ("Beauty and Personal Care", "Skincare, haircare, makeup and grooming tools for daily routines."),
    ("Sports and Fitness", "Cricket, football, badminton, running shoes and kit for a home workout."),
    ("Mobile Phones and Accessories", "Smartphones, chargers, cables, cases, smartwatches and mounts."),
    ("Computers and Laptops", "Laptops, monitors, keyboards, storage and networking for work and play."),
    ("Toys and Games", "Building sets, board games, puzzles, science kits and soft toys."),
    ("Kitchen and Home Appliances", "Mixer grinders, cookers, kettles, coffee makers and other kitchen helpers."),
]

PRODUCTS = {
    "Electronics": [
        ("Arc 3 Wireless Earbuds", "Sonvale", 2499, 3999, 42,
         "wireless earbuds, true wireless, bluetooth 5.3, active noise cancellation, charging case, earphones",
         "Small, light earbuds with active noise cancellation that takes the edge off traffic and office chatter. "
         "You get about seven hours a charge and three more top-ups from the pocket-sized case. Tap controls handle calls, tracks and volume.",
         True, "wireless earbuds charging case"),
        ("Field 700 Over-Ear Headphones", "Sonvale", 6990, 8990, 18,
         "over-ear headphones, wireless headphones, noise cancelling, bluetooth, foldable, 40 hour battery",
         "Closed-back over-ear headphones with soft protein-leather cushions and noise cancelling you can switch off. "
         "A full charge lasts around 40 hours, and they fold flat into the hard case for travel.",
         False, "over ear headphones"),
        ("Pocket Bluetooth Speaker", "Sonvale", 1799, None, 60,
         "bluetooth speaker, portable speaker, waterproof ipx7, outdoor speaker, bass, wireless",
         "A palm-sized speaker with a fabric grille and a strap that clips onto a bag. "
         "It is rated IPX7, so rain and a dunk in the pool are fine, and it plays for about 12 hours.",
         False, "portable bluetooth speaker"),
        ("43-inch 4K Smart TV", "Lumora", 27990, 34990, 9,
         "smart tv, 4k uhd, led television, hdr10, streaming apps, 43 inch tv, wifi",
         "A 43-inch 4K LED panel with HDR10 and the usual streaming apps built in. "
         "Three HDMI ports, Wi-Fi and a slim bezel that suits a bedroom wall or a small living room.",
         True, "flat screen television living room"),
        ("55-inch QLED Smart TV", "Lumora", 46990, 54990, 0,
         "smart tv, qled television, 4k uhd, dolby vision, 55 inch tv, streaming apps",
         "A 55-inch QLED screen with richer colour than a standard LED set and Dolby Vision support. "
         "It has a game mode with low input lag and voice search on the remote.",
         False, "large television screen"),
        ("20000 mAh Power Bank", "Voltrek", 1599, 2199, 75,
         "power bank, portable charger, 20000mah, fast charging, usb-c pd, travel charger",
         "Enough charge to refill most phones four times. "
         "The USB-C port charges at up to 22.5 W in either direction, and two USB-A ports let you top up a second device at the same time.",
         False, "power bank portable charger"),
        ("Snap 24 Mirrorless Camera", "Ferrow", 54990, None, 6,
         "mirrorless camera, 24mp, 4k video, interchangeable lens, kit lens, photography",
         "A 24-megapixel mirrorless body with a 15-45 mm kit lens, fast eye-tracking autofocus and 4K video. "
         "It weighs under 400 grams with the lens on, light enough to carry all day on a trip.",
         False, "mirrorless camera lens"),
        ("Trail Action Camera", "Ferrow", 8499, 10999, 14,
         "action camera, waterproof camera, 4k60, helmet mount, image stabilisation, vlogging",
         "Shoots 4K at 60 frames a second with electronic stabilisation that smooths out bike and trek footage. "
         "Waterproof to 10 metres without a housing, and it ships with a helmet mount and a chest strap.",
         False, "action camera helmet"),
        ("Smart Plug, Pack of 2", "Hearthline", 1299, None, 50,
         "smart plug, wifi plug, voice assistant, schedule, energy monitoring, smart home",
         "Two Wi-Fi plugs that let you switch a geyser, lamp or fan from your phone or by voice. "
         "Set schedules and see how many units each appliance has used this month.",
         False, "smart plug wall socket"),
        ("Indoor Security Camera 2K", "Hearthline", 2199, 2999, 33,
         "security camera, wifi cctv, 2k camera, night vision, two-way audio, smart home",
         "A pan-and-tilt camera that records in 2K, sees in the dark and sends an alert when it spots movement. "
         "Two-way audio lets you talk to whoever is at home, and footage saves to a microSD card.",
         False, "home security camera"),
        ("Soundbar 2.1 with Subwoofer", "Sonvale", 9990, 12990, 11,
         "soundbar, subwoofer, home theatre, tv speaker, dolby audio, hdmi arc",
         "A 2.1 soundbar with a wireless subwoofer that makes TV dialogue clearer and films fuller. "
         "Connect it over HDMI ARC so the TV remote controls the volume.",
         False, "soundbar television"),
    ],
    "Fashion and Clothing": [
        ("Men's Slim-Fit Oxford Shirt", "Indigo Loom", 1299, 1799, 40,
         "men shirt, cotton oxford, slim fit, formal shirt, office wear, button-down",
         "A button-down shirt in soft cotton Oxford weave, cut slim through the body. "
         "It works tucked into chinos for work or open over a T-shirt on weekends.",
         False, "men oxford shirt"),
        ("Women's Block-Print Straight Kurta", "Indigo Loom", 1499, 2199, 35,
         "women kurta, cotton kurta, block print, ethnic wear, straight cut, indian wear",
         "A straight-cut cotton kurta with a hand block-printed floral pattern and three-quarter sleeves. "
         "It pairs with palazzos or jeans and gets softer with every wash.",
         True, "block print kurta"),
        ("Handloom Cotton Saree", "Kaarigar Co.", 3299, None, 12,
         "saree, handloom saree, cotton saree, ethnic wear, zari border, women",
         "Woven on a handloom from fine cotton, with a narrow zari border and a contrast pallu. "
         "Light enough for summer and comes with an unstitched blouse piece.",
         False, "handloom cotton saree"),
        ("Men's Stretch Denim Jeans", "Saltmarsh", 1899, 2499, 48,
         "men jeans, denim, stretch jeans, slim fit, casual wear, five pocket",
         "Mid-rise jeans in dark indigo denim with a little stretch, so they move with you. "
         "Slim through the thigh with a straight leg from the knee down.",
         False, "denim jeans folded"),
        ("Women's High-Rise Wide-Leg Jeans", "Saltmarsh", 1999, None, 22,
         "women jeans, wide leg jeans, high rise, denim, casual wear",
         "High-waisted jeans with a relaxed wide leg in light-wash denim. "
         "The rigid cotton holds its shape and the hem can be cropped without fraying.",
         False, "wide leg jeans"),
        ("Packable Rain Jacket", "Hillcrest Outdoor", 2799, 3499, 25,
         "rain jacket, waterproof jacket, packable jacket, monsoon wear, hooded, outdoor",
         "A waterproof shell with taped seams and an adjustable hood, built for monsoon commutes. "
         "It packs into its own chest pocket and weighs about 300 grams.",
         False, "rain jacket hood"),
        ("Men's Cotton-Silk Nehru Jacket", "Kaarigar Co.", 2499, None, 15,
         "nehru jacket, ethnic wear, men, wedding wear, festive, bandhgala",
         "A sleeveless Nehru jacket in cotton-silk with a mandarin collar and wooden buttons. "
         "Wear it over a kurta for a wedding or over a plain shirt for a festive office day.",
         False, "nehru jacket"),
        ("Unisex Cotton Fleece Hoodie", "Saltmarsh", 1599, None, 44,
         "hoodie, sweatshirt, cotton fleece, unisex, casual wear, winter wear",
         "A heavyweight hoodie in brushed cotton fleece with a kangaroo pocket and ribbed cuffs. "
         "A relaxed fit, in sizes from XS to XXL.",
         False, "grey hoodie"),
        ("Women's Leather Tote Bag", "Thread & Thali", 2999, 3999, 0,
         "tote bag, leather handbag, women bag, office bag, shoulder bag",
         "A structured tote in full-grain leather with an inner zip pocket and space for a 14-inch laptop. "
         "The handles are long enough to carry on the shoulder.",
         False, "leather tote bag"),
        ("Canvas Low-Top Sneakers", "Indigo Loom", 1799, None, 30,
         "sneakers, canvas shoes, casual shoes, unisex, lace-up, white sneakers",
         "Classic low-top sneakers in thick cotton canvas on a vulcanised rubber sole. "
         "The cushioned insole is removable, and they go with nearly everything.",
         False, "white canvas sneakers"),
        ("Women's Minimalist Analog Watch", "Thread & Thali", 3499, 4499, 19,
         "analog watch, women watch, stainless steel, minimalist, wristwatch, accessories",
         "A slim watch with a clean white dial, a sapphire-coated glass and a stainless steel mesh strap. "
         "Water resistant to 30 metres, so hand-washing is no problem.",
         False, "minimalist wrist watch"),
    ],
    "Home and Furniture": [
        ("Solid Sheesham Wood Coffee Table", "Sheesham & Sons", 8999, 11999, 7,
         "coffee table, sheesham wood, solid wood, living room furniture, centre table",
         "A low coffee table made from solid sheesham with a honey finish that shows the wood grain. "
         "The lower shelf holds magazines and remotes, and it arrives fully assembled.",
         True, "wooden coffee table"),
        ("Four-Seater Sheesham Dining Set", "Sheesham & Sons", 32999, None, 4,
         "dining table, dining set, sheesham wood, 4 seater, dining chairs, furniture",
         "A rectangular dining table with four cushioned chairs, all in solid sheesham. "
         "It seats four comfortably and six at a squeeze for festival lunches.",
         False, "wooden dining table chairs"),
        ("Queen Size Cotton Bedsheet Set", "Nestwell", 1199, 1599, 60,
         "bedsheet, cotton bedsheet, queen size, pillow covers, 300 thread count, bedding",
         "A 300-thread-count cotton percale bedsheet with two pillow covers. "
         "Crisp and cool in summer, and the colour holds after many washes.",
         False, "bed sheets bedroom"),
        ("Memory Foam Pillow", "Nestwell", 999, None, 55,
         "pillow, memory foam pillow, neck support, bedroom, sleep, bedding",
         "A contoured memory foam pillow that supports the neck whether you sleep on your back or side. "
         "The bamboo-fabric cover zips off for washing.",
         False, "pillow on bed"),
        ("Three-Seater Fabric Sofa", "Teakhouse", 24999, 31999, 3,
         "sofa, three seater sofa, fabric sofa, living room furniture, couch",
         "A three-seater with deep seats, high-resilience foam and a textured woven fabric in ash grey. "
         "The solid wood frame comes with a five-year warranty.",
         False, "grey fabric sofa"),
        ("Five-Shelf Bookshelf", "Teakhouse", 4499, None, 16,
         "bookshelf, bookcase, engineered wood, storage shelf, five shelves, furniture",
         "A tall, narrow bookshelf in engineered wood with a walnut finish and five fixed shelves. "
         "It fits beside a desk or in a corner and holds around 150 paperbacks.",
         False, "bookshelf with books"),
        ("Blackout Curtains, Pair", "Loomcraft Home", 1399, 1899, 38,
         "curtains, blackout curtains, window curtains, bedroom decor, door curtains",
         "A pair of thick blackout curtains that block most street light and keep rooms cooler in the afternoon. "
         "Eyelet tops slide easily on a standard rod.",
         False, "window curtains room"),
        ("Hand-Tufted Wool Area Rug", "Loomcraft Home", 3999, None, 10,
         "rug, carpet, area rug, hand tufted, wool rug, living room decor",
         "A 4 by 6 foot rug tufted by hand in wool and cotton, with a muted geometric pattern. "
         "Thick enough to soften a tiled floor and easy to vacuum.",
         False, "wool area rug"),
        ("Ceramic Table Lamp", "Nestwell", 1699, None, 27,
         "table lamp, ceramic lamp, bedside lamp, lighting, linen shade, home decor",
         "A glazed ceramic lamp base with a linen drum shade that gives a warm, even glow. "
         "It takes a standard B22 bulb and suits a bedside table or a reading corner.",
         False, "ceramic table lamp"),
        ("Ergonomic Mesh Office Chair", "Teakhouse", 7499, 9999, 0,
         "office chair, ergonomic chair, mesh chair, lumbar support, study chair, furniture",
         "A breathable mesh chair with adjustable lumbar support, armrests and seat height. "
         "The tilt lock and padded seat make long work-from-home days easier on the back.",
         False, "ergonomic office chair"),
        ("Cotton Cushion Covers, Set of 5", "Loomcraft Home", 799, None, 70,
         "cushion covers, cotton cushion covers, living room decor, set of 5, home decor",
         "Five 16-inch cushion covers in woven cotton with hidden zips, in mixed earthy colours. "
         "Wash on a cold cycle.",
         False, "cushions on sofa"),
    ],
    "Books and Stationery": [
        ("The Monsoon Ledger (Novel)", "Margin Books", 399, 499, 80,
         "novel, fiction, paperback, literary fiction, family saga, indian author, book",
         "Meera Kulkarni's debut novel follows three generations of a Konkan family and the account book that holds their secrets. "
         "Paperback, 368 pages.",
         False, "paperback novel book"),
        ("Salt and Signal (Thriller)", "Margin Books", 349, None, 65,
         "thriller, crime fiction, mystery novel, paperback, book, fiction",
         "A radio operator at a Gujarat salt pan picks up a call that should not exist. "
         "A tight coastal thriller by Arjun Bhatt. Paperback, 312 pages.",
         False, "mystery thriller book"),
        ("Grow Your Own Herbs on a Balcony", "Paperleaf Press", 499, None, 40,
         "gardening book, balcony garden, herbs, how-to guide, non-fiction, book",
         "A practical guide to growing tulsi, mint, coriander and twenty other herbs in pots. "
         "Covers soil, watering through the seasons and dealing with pests. Illustrated, 176 pages.",
         False, "herbs in pots balcony"),
        ("Python from First Principles", "Paperleaf Press", 799, 999, 30,
         "programming book, python, coding, computer science, beginners, book",
         "Learn Python by building small, real programs, from a to-do list to a data report. "
         "Written for first-year students with exercises at the end of every chapter. 420 pages.",
         True, "programming book laptop"),
        ("Everyday Indian Vegetarian (Cookbook)", "Paperleaf Press", 699, None, 25,
         "cookbook, vegetarian recipes, indian cooking, recipe book, hardcover, book",
         "One hundred home-style vegetarian recipes from every region, each tested in a small city kitchen. "
         "Hardcover with photographs, 256 pages.",
         False, "cookbook kitchen"),
        ("Fountain Pen, Medium Nib", "Inkwell & Co.", 1250, None, 22,
         "fountain pen, ink pen, calligraphy, writing pen, stationery, medium nib",
         "A brass fountain pen with a smooth steel medium nib and a converter for bottled ink. "
         "Weighted for long writing sessions and comes in a gift box.",
         False, "fountain pen writing"),
        ("Gel Pens, Pack of 10", "Inkwell & Co.", 199, None, 150,
         "gel pens, pens, stationery, school supplies, office supplies, 0.5 mm",
         "Ten 0.5 mm gel pens that write smoothly and dry fast, so they do not smudge. "
         "Six blue, two black, one red, one green.",
         False, "gel pens"),
        ("A5 Dotted Notebook, Hardbound", "Scribe Supply", 349, None, 90,
         "notebook, dotted notebook, a5 journal, bullet journal, hardbound, stationery",
         "A hardbound A5 notebook with 192 pages of 100 gsm dotted paper that takes fountain pen ink without bleeding. "
         "Lay-flat binding, a ribbon marker and a back pocket.",
         False, "dotted notebook journal"),
        ("Watercolour Set, 24 Colours", "Scribe Supply", 899, 1199, 0,
         "watercolour, paint set, art supplies, painting, brushes, artist",
         "Twenty-four half pans of bright, mixable watercolour in a metal tin with a fold-out palette. "
         "Includes two round brushes and a water brush.",
         False, "watercolour paint set"),
        ("Bamboo Desk Organiser", "Scribe Supply", 649, None, 34,
         "desk organiser, stationery holder, office desk, desk storage, bamboo",
         "A bamboo organiser with slots for pens, a phone stand and a small drawer for clips and sticky notes. "
         "Keeps a study desk clear.",
         False, "desk organizer pens"),
        ("Tara and the Tiger Moth (Picture Book)", "Margin Books", 299, None, 45,
         "children book, picture book, kids book, bedtime story, ages 3 to 6",
         "A gently funny bedtime story about a girl who follows a moth around her grandmother's garden. "
         "Full-colour illustrations, 32 pages, for ages 3 to 6.",
         False, "children picture book"),
    ],
    "Beauty and Personal Care": [
        ("Neem and Tea Tree Face Wash", "Neem & Ash", 249, None, 120,
         "face wash, neem, tea tree, oily skin, acne, skincare, cleanser",
         "A gel face wash with neem and tea tree that clears oil without leaving skin tight. "
         "Good for oily and acne-prone skin, twice a day.",
         False, "face wash tube"),
        ("10% Vitamin C Face Serum", "Dewlab", 699, 999, 50,
         "vitamin c serum, face serum, brightening, skincare, dark spots, glow",
         "A lightweight serum with 10% vitamin C and ferulic acid to brighten dull skin and fade dark spots over a few weeks. "
         "Use in the morning under sunscreen.",
         True, "serum dropper bottle"),
        ("SPF 50 Sunscreen Gel", "Dewlab", 499, None, 64,
         "sunscreen, spf 50, sun protection, gel sunscreen, skincare, uva uvb",
         "A broad-spectrum SPF 50 PA++++ gel that sinks in quickly with no white cast. "
         "Works well on oily skin and under makeup.",
         False, "sunscreen bottle"),
        ("Kumkumadi Face Oil", "Kesari Botanicals", 899, None, 21,
         "face oil, kumkumadi, ayurvedic skincare, saffron, glow, night oil",
         "An Ayurvedic night oil with saffron, sandalwood and manjistha. "
         "A few drops pressed into damp skin before bed leave it soft by morning.",
         False, "face oil dropper"),
        ("Onion Hair Oil", "Mitti Naturals", 349, 449, 80,
         "hair oil, onion hair oil, hair fall, hair growth, haircare",
         "A light hair oil with red onion extract and coconut oil that helps cut down hair fall with regular use. "
         "Massage in and leave for an hour or overnight.",
         False, "hair oil bottle"),
        ("Sulphate-Free Shampoo", "Mitti Naturals", 399, None, 70,
         "shampoo, sulphate free shampoo, haircare, frizz control, mild shampoo",
         "A mild shampoo without sulphates or parabens that cleans gently and keeps frizz down. "
         "Safe for coloured hair.",
         False, "shampoo bottle"),
        ("Activated Charcoal Soap, Pack of 4", "Neem & Ash", 299, None, 95,
         "soap, charcoal soap, bath soap, body care, pack of 4",
         "Four bars of cold-processed soap with activated charcoal and neem oil. "
         "A deep clean after a sweaty day without drying the skin.",
         False, "bar soap"),
        ("Hyaluronic Gel Moisturiser", "Dewlab", 549, None, 40,
         "moisturiser, hyaluronic acid, face cream, gel moisturiser, dry skin, skincare",
         "An oil-free gel moisturiser with hyaluronic acid that keeps skin hydrated all day. "
         "Light enough for humid weather.",
         False, "moisturizer cream jar"),
        ("Long-Stay Matte Lipstick", "Kesari Botanicals", 449, None, 36,
         "lipstick, matte lipstick, makeup, long lasting, lip colour",
         "A creamy matte lipstick that stays put through meals for around eight hours. "
         "Enriched with shea butter so lips do not feel dry.",
         False, "lipstick makeup"),
        ("Cordless Beard Trimmer", "Groomwell", 1299, 1799, 28,
         "beard trimmer, trimmer, men grooming, cordless, usb charging",
         "A cordless trimmer with 20 length settings from 0.5 to 10 mm and self-sharpening steel blades. "
         "Runs for 90 minutes on a USB-C charge.",
         False, "beard trimmer"),
        ("Ionic Hair Dryer 1600 W", "Groomwell", 1499, None, 17,
         "hair dryer, ionic hair dryer, hair styling, 1600w, haircare",
         "A 1600 W dryer with ionic care that cuts frizz and drying time. "
         "Two speeds, three heat settings and a cool shot to set the style.",
         False, "hair dryer"),
    ],
    "Sports and Fitness": [
        ("English Willow Cricket Bat", "Cricrest", 6499, 7999, 12,
         "cricket bat, english willow, cricket, full size bat, sports",
         "A Grade 2 English willow bat with eight straight grains, a thick edge and a mid-low sweet spot. "
         "Comes knocked-in and ready to play, with a padded cover.",
         True, "cricket bat"),
        ("Leather Cricket Ball, Pack of 2", "Cricrest", 899, None, 40,
         "cricket ball, leather ball, cricket, match ball, red ball",
         "Two hand-stitched leather balls in red, made for club matches and net practice. "
         "The seam holds up well over a full season.",
         False, "red cricket ball"),
        ("Men's Cushioned Running Shoes", "Stridewell", 2999, 4499, 35,
         "running shoes, sports shoes, men, cushioning, jogging, breathable mesh",
         "Light running shoes with a breathable mesh upper and a soft foam midsole for daily runs and long walks. "
         "The rubber outsole grips on wet roads.",
         False, "running shoes"),
        ("Women's Cross-Training Shoes", "Stridewell", 2799, None, 26,
         "training shoes, gym shoes, women, sports shoes, cross training",
         "Stable trainers with a flat, grippy sole for gym sessions, HIIT and court sports. "
         "A wide toe box gives room to spread out on lifts.",
         False, "training shoes gym"),
        ("Anti-Slip Yoga Mat, 6 mm", "Peakform", 899, 1299, 70,
         "yoga mat, exercise mat, 6mm mat, anti-slip, fitness, workout",
         "A 6 mm TPE mat with a textured surface that stays grippy when you sweat. "
         "Cushioned enough for knees and comes with a carry strap.",
         False, "yoga mat"),
        ("Adjustable Dumbbells, 20 kg Set", "Peakform", 4999, None, 9,
         "dumbbells, adjustable dumbbell, weights, home gym, strength training",
         "A pair of spin-lock dumbbells with plates that add up to 20 kg in total. "
         "Plates have a rubber coating that is quieter on the floor.",
         False, "dumbbells weights"),
        ("Resistance Bands, Set of 5", "Peakform", 699, None, 55,
         "resistance bands, workout bands, home workout, fitness, strength training",
         "Five latex loop bands from light to extra heavy for warm-ups, glute work and physio exercises. "
         "Comes with a pouch and an exercise chart.",
         False, "resistance bands exercise"),
        ("Anti-Fog Swimming Goggles", "Aquelle", 549, None, 48,
         "swimming goggles, anti-fog, swimming, uv protection, adjustable strap",
         "Low-profile goggles with anti-fog coated lenses, UV protection and soft silicone seals. "
         "The split strap stays put during laps.",
         False, "swimming goggles"),
        ("Graphite Badminton Racquet", "Stridewell", 1399, 1899, 30,
         "badminton racquet, badminton, graphite racquet, sports, shuttle",
         "A light 85 g graphite racquet, strung and balanced for quick defence at the net. "
         "Comes with a full-length cover.",
         False, "badminton racket"),
        ("Foldable Motorised Treadmill", "Peakform", 22999, 27999, 0,
         "treadmill, foldable treadmill, cardio, home gym, running, motorised",
         "A 2 HP treadmill that folds upright to save space, with speeds up to 12 km/h and three incline levels. "
         "The display shows time, distance, speed and calories.",
         False, "treadmill"),
        ("Training Football, Size 5", "Cricrest", 799, None, 42,
         "football, size 5 ball, soccer ball, training ball, sports",
         "A machine-stitched size 5 ball with a rubber bladder that keeps its shape on rough grounds. "
         "Good for practice and five-a-side.",
         False, "soccer ball grass"),
    ],
    "Mobile Phones and Accessories": [
        ("Nova 5G Smartphone, 8 GB / 128 GB", "Orvia", 18999, 21999, 24,
         "smartphone, 5g phone, android phone, 128gb, 50mp camera, mobile phone, 5000mah",
         "A 5G phone with a 6.6-inch 120 Hz display, a 50 MP main camera and a 5000 mAh battery that lasts a full day and more. "
         "8 GB RAM and 128 GB storage.",
         True, "smartphone in hand"),
        ("Nova Pro 5G, 12 GB / 256 GB", "Orvia", 29999, 33999, 13,
         "smartphone, 5g phone, amoled display, 256gb, flagship phone, mobile phone",
         "The bigger sibling of the Nova with a curved AMOLED screen, optical stabilisation on the main camera and 67 W charging. "
         "12 GB RAM and 256 GB storage.",
         False, "smartphone screen"),
        ("Lite 4G, 4 GB / 64 GB", "Orvia", 8999, None, 31,
         "budget smartphone, 4g phone, android phone, 64gb, 5000mah battery, mobile phone",
         "A dependable budget phone with a large 6.5-inch screen, two-day battery life and dual SIM slots. "
         "4 GB RAM and 64 GB storage, expandable by microSD.",
         False, "mobile phone table"),
        ("33 W USB-C Fast Charger", "Chargelink", 899, None, 85,
         "fast charger, usb-c charger, 33w charger, mobile charger, wall adapter",
         "A compact 33 W wall charger with power delivery that takes most phones from flat to half in about 30 minutes. "
         "Works with laptops and tablets that charge over USB-C.",
         False, "usb charger adapter"),
        ("Braided USB-C Cable, 1.5 m", "Chargelink", 349, None, 140,
         "usb-c cable, charging cable, braided cable, data cable, fast charging",
         "A nylon-braided USB-C to USB-C cable rated for 60 W charging and fast data transfer. "
         "Tested to survive 10,000 bends.",
         False, "usb cable"),
        ("Tempered Glass Screen Protector for Nova", "ShieldGuard", 299, None, 110,
         "screen protector, tempered glass, phone protection, 9h hardness, mobile accessories",
         "A 9H tempered glass protector cut to fit the Orvia Nova, with an oil-resistant coating. "
         "Includes an alignment frame so it goes on straight the first time.",
         False, "phone screen protector"),
        ("Rugged Case for Nova", "ShieldGuard", 499, None, 66,
         "phone case, back cover, rugged case, shockproof, mobile cover",
         "A shockproof case with air-cushioned corners and raised edges around the camera and screen. "
         "Slim enough to fit in a pocket.",
         False, "phone case"),
        ("15 W Wireless Charging Pad", "Chargelink", 1199, 1499, 0,
         "wireless charger, qi charger, charging pad, fast wireless charging",
         "A Qi wireless pad that charges compatible phones at up to 15 W, even through a thin case. "
         "A soft light shows when it is charging and turns off at night.",
         False, "wireless charging pad"),
        ("Fit Smartwatch with Calling", "Orvia", 3499, 4999, 29,
         "smartwatch, fitness tracker, heart rate, spo2, bluetooth calling, watch",
         "A smartwatch with a 1.8-inch display, heart rate and SpO2 tracking, and Bluetooth calling from the wrist. "
         "Battery lasts about a week.",
         False, "smartwatch wrist"),
        ("Magnetic Car Phone Mount", "ShieldGuard", 599, None, 52,
         "car mount, phone holder, dashboard mount, magnetic mount, car accessories",
         "A magnetic mount that sticks to the dashboard and holds a phone steady on bumpy roads. "
         "Rotates 360 degrees for maps in portrait or landscape.",
         False, "phone holder car"),
        ("Bluetooth Selfie Stick Tripod", "Chargelink", 799, None, 40,
         "selfie stick, tripod, bluetooth remote, phone tripod, vlogging",
         "A selfie stick that opens into a stable tripod, with a detachable Bluetooth remote. "
         "Extends to 1 metre and folds down to the size of a torch.",
         False, "phone tripod"),
    ],
    "Computers and Laptops": [
        ("Air 14 Laptop, Ryzen 5, 16 GB, 512 GB SSD", "Corelane", 52990, 59990, 10,
         "laptop, thin and light laptop, ryzen 5, 16gb ram, 512gb ssd, 14 inch, notebook",
         "A thin, 1.3 kg laptop with a sharp 14-inch display, a Ryzen 5 processor, 16 GB RAM and a 512 GB SSD. "
         "The battery lasts a full college or work day.",
         True, "thin laptop desk"),
        ("Pro 16 Laptop, Core i7, 16 GB, 1 TB SSD", "Corelane", 89990, None, 5,
         "laptop, performance laptop, core i7, 1tb ssd, 16 inch, creator laptop, notebook",
         "A 16-inch laptop with a colour-accurate display, a Core i7 processor and a 1 TB SSD, built for photo and video editing. "
         "Full-size keyboard with a number pad.",
         False, "laptop open on desk"),
        ("Gaming Laptop with RTX Graphics", "Bytecraft", 104990, 119990, 0,
         "gaming laptop, rtx graphics, 144hz display, core i7, gaming, laptop",
         "A gaming laptop with RTX graphics, a 144 Hz display and a cooling system that stays quiet in long sessions. "
         "Per-key RGB keyboard.",
         False, "gaming laptop"),
        ("24-inch IPS Monitor, Full HD", "Tessel", 9999, 12499, 20,
         "monitor, 24 inch monitor, ips display, full hd, 75hz, hdmi, computer screen",
         "A 24-inch Full HD IPS monitor with thin bezels and a 75 Hz refresh rate. "
         "HDMI and VGA inputs, and a flicker-free backlight for long hours.",
         False, "computer monitor desk"),
        ("27-inch QHD USB-C Monitor", "Tessel", 17499, None, 8,
         "monitor, 27 inch monitor, qhd, 1440p, usb-c monitor, office monitor",
         "A 27-inch 1440p monitor that charges and connects a laptop over one USB-C cable. "
         "Height-adjustable stand.",
         False, "monitor screen"),
        ("Hot-Swappable Mechanical Keyboard", "Keystrand", 3299, 3999, 26,
         "mechanical keyboard, keyboard, rgb keyboard, hot-swappable, gaming keyboard, typing",
         "A compact 75% mechanical keyboard with hot-swappable switches, PBT keycaps and white backlighting. "
         "Connects by cable or Bluetooth.",
         False, "mechanical keyboard"),
        ("Silent Wireless Mouse", "Keystrand", 799, None, 72,
         "wireless mouse, mouse, silent click, ergonomic mouse, usb receiver",
         "A quiet wireless mouse with soft-click buttons, a contoured shape and a battery that lasts about a year. "
         "Plug-and-play USB receiver.",
         False, "computer mouse"),
        ("1 TB Portable SSD", "Bytecraft", 6499, 7999, 21,
         "portable ssd, external ssd, 1tb storage, usb-c, backup drive",
         "A pocket-sized 1 TB SSD with read speeds up to 1050 MB/s over USB-C. "
         "The aluminium shell handles drops of up to two metres.",
         False, "external hard drive"),
        ("Dual-Band Wi-Fi 6 Router", "Bytecraft", 3999, None, 17,
         "wifi router, wi-fi 6, dual band router, internet, networking, broadband",
         "A Wi-Fi 6 router with four antennas that covers a three-bedroom flat with steady speeds. "
         "Set up in a few minutes from the phone app.",
         False, "wifi router"),
        ("Water-Resistant 15.6-inch Laptop Backpack", "Corelane", 1499, 1999, 46,
         "laptop backpack, laptop bag, 15.6 inch, water resistant, travel backpack",
         "A water-resistant backpack with a padded laptop sleeve, a USB charging port and a hidden back pocket. "
         "Fits a 15.6-inch laptop and a day's things.",
         False, "laptop backpack"),
        ("1080p Webcam with Microphone", "Tessel", 2299, None, 30,
         "webcam, 1080p webcam, video calls, microphone, usb webcam, streaming",
         "A Full HD webcam with autofocus, light correction and two microphones for clear video calls. "
         "Clips onto any monitor or laptop screen.",
         False, "webcam on monitor"),
    ],
    "Toys and Games": [
        ("City Fire Station Building Set, 720 Pieces", "Brickyard", 3499, 4299, 15,
         "building blocks, construction toy, building set, bricks, kids, ages 7 and up",
         "A 720-piece building set with a fire station, a truck with a working ladder and four minifigures. "
         "Step-by-step instructions, for ages 7 and up.",
         True, "toy building blocks"),
        ("Starter Bricks Bucket, 300 Pieces", "Brickyard", 1299, None, 40,
         "building blocks, bricks, creative toy, kids, ages 4 and up, construction toy",
         "A tub of 300 bricks in bright colours with wheels, windows and two baseplates. "
         "Open-ended play for ages 4 and up.",
         False, "colorful toy bricks"),
        ("Wooden Chess Set", "Gameshala", 1199, None, 25,
         "chess set, board game, wooden chess, strategy game, chess",
         "A folding wooden board with weighted Staunton pieces stored inside. "
         "A 30 cm board that is good for learning and for travel.",
         False, "wooden chess board"),
        ("Ludo and Snakes and Ladders, 2-in-1", "Gameshala", 399, None, 60,
         "ludo, snakes and ladders, board game, family game, kids",
         "A double-sided board with Ludo on one side and Snakes and Ladders on the other. "
         "Includes counters and two dice for up to four players.",
         False, "ludo board game"),
        ("Full-Size Carrom Board", "Gameshala", 2999, 3599, 9,
         "carrom board, indoor game, family game, wooden board, carrom",
         "A full-size carrom board with a smooth playing surface, solid wood frame and a set of coins and striker. "
         "Board size 32 inches square.",
         False, "carrom board"),
        ("Remote Control Racing Car", "Tinkerbox", 1899, None, 22,
         "rc car, remote control car, racing car, toy car, rechargeable, kids",
         "A 1:18 scale racing car that reaches 20 km/h, with a rechargeable battery and a 2.4 GHz remote. "
         "Rubber tyres grip indoors and out.",
         False, "remote control car toy"),
        ("Solar Robot Science Kit", "Tinkerbox", 999, None, 34,
         "science kit, stem toy, solar robot, educational toy, diy kit, kids",
         "Build 12 different solar-powered robots from one kit, from a crawling bug to a boat. "
         "No batteries needed; for ages 8 and up.",
         False, "robot toy kit"),
        ("Soft Teddy Bear, 40 cm", "Little Lantern", 699, None, 50,
         "teddy bear, soft toy, plush toy, gift, kids",
         "A 40 cm teddy in super-soft plush with stitched eyes, safe for small children. "
         "Machine washable on a gentle cycle.",
         False, "teddy bear"),
        ("Wooden Stacking Rings", "Little Lantern", 449, None, 0,
         "stacking toy, wooden toy, toddler toy, montessori, ages 1 and up",
         "Seven rainbow rings on a wooden post, finished with child-safe paint. "
         "Helps toddlers practise grip and sizes.",
         False, "wooden stacking toy"),
        ("1000-Piece Jigsaw Puzzle, Spice Market", "Gameshala", 799, None, 28,
         "jigsaw puzzle, 1000 pieces, puzzle, adults, family, spice market",
         "A 1000-piece puzzle of a crowded spice market, printed on thick board so pieces do not bend. "
         "Comes with a poster for reference.",
         False, "jigsaw puzzle pieces"),
        ("Three-Wheel Kick Scooter", "Tinkerbox", 2499, 2999, 14,
         "kick scooter, kids scooter, 3 wheel scooter, outdoor toy, adjustable",
         "A three-wheel scooter with light-up wheels and a handlebar that grows with the child. "
         "Lean-to-steer makes balancing easy for ages 3 to 8.",
         False, "kids scooter"),
    ],
    "Kitchen and Home Appliances": [
        ("Mixer Grinder 750 W, 3 Jars", "Tadka Home", 3499, 4999, 30,
         "mixer grinder, 750w mixer, kitchen appliance, jars, chutney, grinding",
         "A 750 W mixer grinder with three stainless steel jars for wet grinding, dry masalas and chutneys. "
         "Overload protection and a five-year motor warranty.",
         True, "mixer grinder kitchen"),
        ("Stainless Steel Pressure Cooker, 5 L", "Steelwell", 1899, 2299, 44,
         "pressure cooker, stainless steel cooker, 5 litre, induction base, cookware",
         "A 5-litre stainless steel cooker with an induction base and a gasket-release safety valve. "
         "Right for dal, rice and curries for a family of four.",
         False, "pressure cooker"),
        ("Non-Stick Dosa Tawa, 28 cm", "Steelwell", 799, None, 55,
         "tawa, non-stick tawa, dosa tawa, cookware, induction compatible",
         "A 28 cm tawa with a three-layer non-stick coating for thin dosas and soft rotis with little oil. "
         "Works on gas and induction.",
         False, "frying pan tawa"),
        ("Drip Coffee Maker", "Brewmate", 2799, None, 18,
         "coffee maker, drip coffee, filter coffee, kitchen appliance, coffee",
         "A drip coffee maker that brews up to six cups and keeps them warm for 40 minutes. "
         "The reusable mesh filter means no paper filters to buy.",
         False, "coffee maker"),
        ("Electric Kettle, 1.5 L", "Brewmate", 1099, 1399, 62,
         "electric kettle, kettle, 1.5 litre, stainless steel, tea, kitchen appliance",
         "A 1.5-litre stainless steel kettle that boils water in about four minutes and switches off on its own. "
         "Handy for tea, instant noodles and baby bottles.",
         False, "electric kettle"),
        ("Digital Air Fryer, 4.2 L", "Tadka Home", 4999, 6499, 12,
         "air fryer, digital air fryer, 4.2 litre, oil-free cooking, kitchen appliance",
         "A 4.2-litre air fryer with eight presets that crisps samosas, fries and tikkas with a spoon of oil. "
         "The basket is non-stick and dishwasher safe.",
         False, "air fryer"),
        ("Table-Top Wet Grinder, 2 L", "Chakki Pro", 6499, None, 7,
         "wet grinder, idli batter, dosa batter, stone grinder, kitchen appliance",
         "A 2-litre wet grinder with granite stones that makes smooth idli and dosa batter. "
         "The drum lifts out for easy washing.",
         False, "wet grinder"),
        ("Induction Cooktop, 2000 W", "Steelwell", 2299, None, 25,
         "induction cooktop, induction stove, 2000w, cooking, kitchen appliance",
         "A 2000 W induction cooktop with Indian menu presets, a timer and a feather-touch panel. "
         "Heats faster than gas and is easy to wipe clean.",
         False, "induction cooktop"),
        ("Solo Microwave Oven, 20 L", "Tadka Home", 6999, None, 11,
         "microwave oven, solo microwave, 20 litre, reheat, defrost, kitchen appliance",
         "A 20-litre solo microwave for reheating, defrosting and quick cooking. "
         "Five power levels and an auto-cook menu.",
         False, "microwave oven"),
        ("RO + UV Water Purifier", "Steelwell", 12999, 15999, 6,
         "water purifier, ro uv purifier, drinking water, kitchen appliance",
         "A wall-mounted RO and UV purifier with an 8-litre tank for safe drinking water from borewell or municipal supply. "
         "A filter-change alert reminds you when it is due.",
         False, "water purifier"),
        ("Hand Blender, 400 W", "Brewmate", 1299, None, 36,
         "hand blender, immersion blender, 400w, soups, smoothies, kitchen appliance",
         "A 400 W hand blender with a stainless steel shaft for soups, smoothies and lassi right in the pot or glass. "
         "Two speeds and a turbo button.",
         False, "hand blender"),
    ],
}

DEMO_CUSTOMERS = [
    # (name, email, mobile_number, address)
    ("Asha Rao", "asha.rao@example.com", "9876501234", "14 Lakeview Apartments, Baner Road, Pune, Maharashtra 411045"),
    ("Rahul Menon", "rahul.menon@example.com", "9847012345", "TC 22/1180, Kowdiar, Thiruvananthapuram, Kerala 695003"),
    ("Priya Sharma", "priya.sharma@example.com", "9829034567", "B-7 Shanti Nagar, Jaipur, Rajasthan 302006"),
    ("Imran Qureshi", "imran.qureshi@example.com", "9908045678", "Flat 302, Banjara Heights, Hyderabad, Telangana 500034"),
]
