"""
Platform adapters — every product is a self-consistent unit:
title + image_search_term + price_range all come from the same product definition.
No random brand/suffix mixing that produces mismatched data.
"""
import random
import asyncio
from typing import List, Optional
from urllib.parse import quote_plus
from app.schemas.product import ProductSchema
from app.agents.product_search.base_adapter import BaseAdapter

# ── Self-consistent product catalog ──────────────────────────────────────────
# Each entry: (title_template, image_search_term, price_lo, price_hi)
# title_template uses {q} for the search query where needed.
# image_search_term is what gets sent to Openverse — must match the product.
_CATALOG = {
    # ── Laptops ──
    "laptop": [
        ("HP Pavilion 15 Laptop",              "HP Pavilion laptop",          35000,  55000),
        ("Dell Inspiron 15 Laptop",            "Dell Inspiron laptop",        40000,  65000),
        ("Lenovo IdeaPad Slim 3 Laptop",       "Lenovo IdeaPad laptop",       35000,  55000),
        ("Asus VivoBook 15 Laptop",            "Asus VivoBook laptop",        38000,  60000),
        ("Acer Aspire 5 Laptop",               "Acer Aspire laptop",          32000,  52000),
        ("Apple MacBook Air M2",               "Apple MacBook Air",           99900, 134900),
        ("Apple MacBook Pro 14",               "Apple MacBook Pro",          149900, 249900),
        ("HP Envy x360 Laptop",                "HP Envy laptop",              65000,  85000),
        ("Dell XPS 13 Laptop",                 "Dell XPS laptop",             90000, 130000),
        ("Lenovo ThinkPad E14 Laptop",         "Lenovo ThinkPad laptop",      55000,  80000),
    ],
    # ── Phones ──
    "phone": [
        ("Apple iPhone 15",                    "Apple iPhone 15",             59999,  89999),
        ("Samsung Galaxy S23",                 "Samsung Galaxy S23",          49999,  79999),
        ("OnePlus 12",                         "OnePlus 12 smartphone",       64999,  74999),
        ("Redmi Note 13 Pro",                  "Redmi Note 13 Pro",           14999,  24999),
        ("Realme 12 Pro",                      "Realme 12 Pro smartphone",    12999,  19999),
        ("Google Pixel 8",                     "Google Pixel 8",              59999,  89999),
        ("Vivo V29 Pro",                       "Vivo V29 Pro smartphone",     35999,  45999),
        ("Oppo Reno 11 Pro",                   "Oppo Reno 11 Pro",            29999,  39999),
        ("Motorola Edge 40",                   "Motorola Edge 40",            19999,  29999),
        ("Nokia G42 5G",                       "Nokia G42 smartphone",         9999,  14999),
    ],
    # ── iPhones ──
    "iphone": [
        ("Apple iPhone 16 Pro Max",            "Apple iPhone 16 Pro Max",    119900, 134900),
        ("Apple iPhone 16 Pro",                "Apple iPhone 16 Pro",         99900, 119900),
        ("Apple iPhone 16",                    "Apple iPhone 16",             79999,  99900),
        ("Apple iPhone 15 Pro Max",            "Apple iPhone 15 Pro Max",     89999, 109900),
        ("Apple iPhone 15 Pro",                "Apple iPhone 15 Pro",         79999,  89999),
        ("Apple iPhone 15",                    "Apple iPhone 15",             59999,  79999),
        ("Apple iPhone 14",                    "Apple iPhone 14",             49999,  69999),
        ("Apple iPhone 13",                    "Apple iPhone 13",             39999,  59999),
    ],
    # ── Samsung phones ──
    "samsung": [
        ("Samsung Galaxy S24 Ultra",           "Samsung Galaxy S24 Ultra",    99999, 134900),
        ("Samsung Galaxy S24+",                "Samsung Galaxy S24 Plus",     74999,  99999),
        ("Samsung Galaxy S24",                 "Samsung Galaxy S24",          59999,  79999),
        ("Samsung Galaxy A55 5G",              "Samsung Galaxy A55",          29999,  39999),
        ("Samsung Galaxy A35 5G",              "Samsung Galaxy A35",          19999,  29999),
        ("Samsung Galaxy M34 5G",              "Samsung Galaxy M34",          14999,  19999),
        ("Samsung Galaxy F55 5G",              "Samsung Galaxy F55",          24999,  34999),
        ("Samsung Galaxy Z Fold 5",            "Samsung Galaxy Z Fold",      149900, 179900),
    ],
    # ── Headphones ──
    "headphones": [
        ("Sony WH-1000XM5 Headphones",         "Sony WH-1000XM5 headphones",  24999,  34999),
        ("Bose QuietComfort 45 Headphones",    "Bose QuietComfort headphones",24999,  34999),
        ("JBL Tune 770NC Headphones",          "JBL Tune headphones",          5999,   9999),
        ("Boat Rockerz 550 Headphones",        "Boat Rockerz headphones",      1499,   2999),
        ("Sennheiser HD 450BT Headphones",     "Sennheiser HD headphones",     7999,  12999),
        ("Audio-Technica ATH-M50x",            "Audio-Technica ATH headphones",8999,  14999),
        ("Skullcandy Crusher ANC 2",           "Skullcandy Crusher headphones",9999,  14999),
        ("Oneplus Bullets Z2 Headphones",      "OnePlus Bullets headphones",   1999,   3999),
    ],
    # ── Earbuds ──
    "earbuds": [
        ("Apple AirPods Pro 2nd Gen",          "Apple AirPods Pro",           24900,  26900),
        ("Samsung Galaxy Buds2 Pro",           "Samsung Galaxy Buds Pro",     12999,  17999),
        ("Sony WF-1000XM5 Earbuds",            "Sony WF earbuds",             19999,  24999),
        ("Boat Airdopes 141 Earbuds",          "Boat Airdopes earbuds",         999,   1999),
        ("JBL Tune 230NC TWS Earbuds",         "JBL Tune earbuds",             3999,   5999),
        ("Noise Buds VS104 Earbuds",           "Noise Buds earbuds",            999,   1999),
        ("Realme Buds Air 5 Pro",              "Realme Buds earbuds",          2999,   4999),
        ("OnePlus Nord Buds 2",                "OnePlus Nord Buds earbuds",    2999,   3999),
    ],
    # ── Shoes ──
    "shoes": [
        ("Nike Air Max 270 Running Shoes",     "Nike Air Max shoes",           6999,  12999),
        ("Adidas Ultraboost 22 Shoes",         "Adidas Ultraboost shoes",      7999,  14999),
        ("Puma Softride Enzo Shoes",           "Puma Softride shoes",          2999,   5999),
        ("Reebok Floatride Energy Shoes",      "Reebok Floatride shoes",       4999,   8999),
        ("New Balance Fresh Foam Shoes",       "New Balance Fresh Foam shoes", 5999,  10999),
        ("Skechers Go Walk 6 Shoes",           "Skechers Go Walk shoes",       2999,   5999),
        ("Bata Power Shoes",                   "Bata Power shoes",              999,   2999),
        ("Red Tape Sports Shoes",              "Red Tape sports shoes",        1999,   3999),
    ],
    # ── Sneakers ──
    "sneakers": [
        ("Nike Air Force 1 Sneakers",          "Nike Air Force 1 sneakers",    6999,  10999),
        ("Adidas Stan Smith Sneakers",         "Adidas Stan Smith sneakers",   5999,   9999),
        ("Puma Suede Classic Sneakers",        "Puma Suede sneakers",          3999,   6999),
        ("Converse Chuck Taylor Sneakers",     "Converse Chuck Taylor",        3999,   6999),
        ("Vans Old Skool Sneakers",            "Vans Old Skool sneakers",      4999,   7999),
        ("New Balance 574 Sneakers",           "New Balance 574 sneakers",     5999,   9999),
        ("Reebok Classic Leather Sneakers",    "Reebok Classic sneakers",      3999,   6999),
        ("Fila Disruptor Sneakers",            "Fila Disruptor sneakers",      2999,   4999),
    ],
    # ── Laptop bag ──
    "laptop bag": [
        ("Wildcraft Nylon Laptop Backpack",    "Wildcraft laptop backpack",     799,   1999),
        ("Skybags Bingo Laptop Bag",           "Skybags laptop bag",            599,   1499),
        ("American Tourister Laptop Bag",      "American Tourister laptop bag", 999,   2499),
        ("Safari Laptop Backpack",             "Safari laptop backpack",        699,   1799),
        ("HP Active Laptop Backpack",          "HP laptop backpack",            999,   1999),
        ("Dell Professional Laptop Bag",       "Dell laptop bag",              1299,   2499),
        ("Lenovo Laptop Sleeve Bag",           "Lenovo laptop sleeve bag",      599,   1299),
        ("Targus Classic Laptop Bag",          "Targus laptop bag",            1499,   2999),
    ],
    # ── Backpack ──
    "backpack": [
        ("Wildcraft Trailblazer Backpack",     "Wildcraft backpack",           1499,   3499),
        ("Skybags Footloose Backpack",         "Skybags backpack",              999,   2499),
        ("American Tourister Backpack",        "American Tourister backpack",  1499,   3499),
        ("Quechua Hiking Backpack 20L",        "Quechua hiking backpack",      1999,   4999),
        ("Nike Brasilia Training Backpack",    "Nike Brasilia backpack",       2999,   4999),
        ("Adidas Classic Backpack",            "Adidas Classic backpack",      2499,   4499),
        ("Puma Phase Backpack",                "Puma Phase backpack",          1999,   3499),
        ("F Gear Backpack",                    "F Gear backpack",               799,   1999),
    ],
    # ── Smartwatch ──
    "smartwatch": [
        ("Apple Watch Series 9",               "Apple Watch Series 9",        41900,  89900),
        ("Samsung Galaxy Watch 6",             "Samsung Galaxy Watch 6",      24999,  39999),
        ("Garmin Venu 3 Smartwatch",           "Garmin Venu smartwatch",      34999,  49999),
        ("Fitbit Versa 4 Smartwatch",          "Fitbit Versa smartwatch",     14999,  19999),
        ("Noise ColorFit Pro 4 Smartwatch",    "Noise ColorFit smartwatch",    1999,   3999),
        ("boAt Xtend Pro Smartwatch",          "Boat Xtend smartwatch",        1999,   3499),
        ("Amazfit GTR 4 Smartwatch",           "Amazfit GTR smartwatch",       9999,  14999),
        ("Titan Smart Smartwatch",             "Titan Smart smartwatch",       4999,   9999),
    ],
    # ── Refrigerator ──
    "refrigerator": [
        ("Samsung 253L Double Door Refrigerator",  "Samsung double door refrigerator", 22000, 35000),
        ("LG 260L Double Door Refrigerator",       "LG double door refrigerator",      24000, 38000),
        ("Whirlpool 265L Triple Door Refrigerator","Whirlpool refrigerator",           26000, 40000),
        ("Haier 195L Single Door Refrigerator",    "Haier single door refrigerator",   12000, 18000),
        ("Godrej 190L Single Door Refrigerator",   "Godrej refrigerator",              12000, 17000),
        ("Bosch 559L Side-by-Side Refrigerator",   "Bosch side by side refrigerator",  65000, 90000),
        ("Voltas Beko 340L Refrigerator",          "Voltas Beko refrigerator",         28000, 40000),
        ("IFB 256L Double Door Refrigerator",      "IFB double door refrigerator",     22000, 32000),
    ],
    # ── Washing machine ──
    "washing machine": [
        ("Samsung 7kg Front Load Washing Machine",  "Samsung front load washing machine", 28000, 45000),
        ("LG 8kg Front Load Washing Machine",       "LG front load washing machine",      32000, 50000),
        ("Whirlpool 7.5kg Top Load Washing Machine","Whirlpool top load washing machine", 18000, 28000),
        ("Bosch 8kg Front Load Washing Machine",    "Bosch front load washing machine",   35000, 55000),
        ("IFB 6.5kg Front Load Washing Machine",    "IFB front load washing machine",     25000, 38000),
        ("Haier 7kg Top Load Washing Machine",      "Haier top load washing machine",     15000, 22000),
        ("Godrej 7kg Top Load Washing Machine",     "Godrej top load washing machine",    14000, 20000),
        ("Voltas Beko 8kg Front Load",              "Voltas Beko washing machine",        28000, 42000),
    ],
    # ── TV ──
    "tv": [
        ("Samsung 55\" 4K QLED Smart TV",      "Samsung QLED 4K TV",          55000,  90000),
        ("LG 55\" OLED 4K Smart TV",           "LG OLED 4K TV",               80000, 150000),
        ("Sony Bravia 55\" 4K Smart TV",       "Sony Bravia 4K TV",           55000,  90000),
        ("Mi 43\" 4K Ultra HD Smart TV",       "Xiaomi Mi 4K Smart TV",       22000,  35000),
        ("OnePlus 50\" Y1S Pro Smart TV",      "OnePlus Y1S Smart TV",        28000,  42000),
        ("TCL 55\" QLED 4K Smart TV",          "TCL QLED 4K TV",              35000,  55000),
        ("Hisense 50\" 4K Smart TV",           "Hisense 4K Smart TV",         28000,  42000),
        ("Vu 55\" Premium 4K Smart TV",        "Vu Premium 4K TV",            30000,  45000),
    ],
    # ── Jeans ──
    "jeans": [
        ("Levi's 511 Slim Fit Jeans",          "Levis 511 slim jeans",         2999,   5999),
        ("Wrangler Regular Fit Jeans",         "Wrangler regular jeans",       1999,   3999),
        ("Lee Regular Fit Jeans",              "Lee regular fit jeans",        2499,   4499),
        ("Pepe Jeans Slim Fit",                "Pepe Jeans slim fit",          2499,   4999),
        ("Jack & Jones Slim Fit Jeans",        "Jack Jones slim jeans",        2999,   5499),
        ("Roadster Skinny Fit Jeans",          "Roadster skinny jeans",        1499,   2999),
        ("H&M Slim Fit Jeans",                 "HM slim fit jeans",            1999,   3499),
        ("Spykar Slim Fit Jeans",              "Spykar slim jeans",            1999,   3999),
    ],
    # ── Shirt ──
    "shirt": [
        ("Allen Solly Regular Fit Shirt",      "Allen Solly formal shirt",     1499,   2999),
        ("Van Heusen Slim Fit Shirt",          "Van Heusen slim shirt",        1499,   2999),
        ("Arrow Regular Fit Shirt",            "Arrow formal shirt",           1499,   2999),
        ("Peter England Slim Fit Shirt",       "Peter England shirt",          1299,   2499),
        ("Louis Philippe Formal Shirt",        "Louis Philippe formal shirt",  1999,   3999),
        ("Raymond Regular Fit Shirt",          "Raymond formal shirt",         1999,   3499),
        ("Park Avenue Slim Fit Shirt",         "Park Avenue shirt",            1499,   2999),
        ("Blackberrys Formal Shirt",           "Blackberrys formal shirt",     1499,   2999),
    ],
    # ── Water bottle ──
    "water bottle": [
        ("Milton Thermosteel Water Bottle 1L", "Milton Thermosteel bottle",     599,   1299),
        ("Cello Puro Steel Water Bottle",      "Cello steel water bottle",      299,    699),
        ("Nalgene Wide Mouth Water Bottle",    "Nalgene water bottle",          999,   1999),
        ("Hydro Flask Water Bottle 32oz",      "Hydro Flask water bottle",     2999,   4999),
        ("Tupperware Eco Bottle",              "Tupperware water bottle",       499,    999),
        ("Borosil Hydra Trek Bottle",          "Borosil water bottle",          599,   1299),
        ("Puma Training Water Bottle",         "Puma sports water bottle",      499,    999),
        ("Decathlon Tritan Water Bottle",      "Decathlon water bottle",        399,    799),
    ],
}

# Fallback catalog for queries not in _CATALOG — uses query itself as image search term
_FALLBACK_BRANDS = [
    "Samsung", "Sony", "HP", "Dell", "LG", "Bosch", "Philips",
    "Panasonic", "Whirlpool", "Haier",
]


def _get_catalog_key(query: str) -> Optional[str]:
    """Find the best matching catalog key for a query."""
    q = query.lower().strip()
    # Exact match first
    if q in _CATALOG:
        return q
    # Substring match — longest key wins
    matches = [k for k in _CATALOG if k in q or q in k]
    if matches:
        return max(matches, key=len)
    return None


def _mock_products(platform: str, query: str, count: int, category: str) -> List[dict]:
    """Generate self-consistent products where title+image+price+URL all match."""
    from app.agents.product_search.adapters import platform_priority
    priority = platform_priority(platform, category)
    catalog_key = _get_catalog_key(query)
    entries = _CATALOG.get(catalog_key, []) if catalog_key else []

    products = []
    for i in range(count):
        seed = sum(ord(c) for c in (platform + query).lower()) + i * 31
        random.seed(seed)

        if entries:
            entry = entries[i % len(entries)]
            title, img_term, price_lo, price_hi = entry
            mid = price_lo + (price_hi - price_lo) * 0.6
            base_price = random.uniform(price_lo, mid)
            # small platform variation ±5%
            price = max(price_lo, round(base_price * random.uniform(0.95, 1.05) / 10) * 10)
        else:
            # Fallback: brand + query title
            brand = _FALLBACK_BRANDS[i % len(_FALLBACK_BRANDS)]
            title = f"{brand} {query.title()}"
            img_term = f"{brand} {query}"
            price = round(random.uniform(500, 50000) / 10) * 10

        original = round(price * random.uniform(1.1, 1.35) / 10) * 10
        discount = round((original - price) / original * 100, 1)
        rating = round(random.uniform(3.5, 5.0), 1)
        review_count = random.randint(100, 25000)
        availability = random.choices([True, False], weights=[85, 15])[0]
        delivery = random.choice(["Same day", "1-2 days", "2-3 days", "3-5 days"])
        random.seed()

        # product_url: Google I'm Feeling Lucky scoped to platform — opens exact product page
        site = {
            "Amazon": "site:amazon.in", "Flipkart": "site:flipkart.com",
            "Meesho": "site:meesho.com", "Myntra": "site:myntra.com",
            "Ajio": "site:ajio.com", "Croma": "site:croma.com",
            "Reliance Digital": "site:reliancedigital.in",
        }.get(platform, "")
        product_url = f"https://www.google.com/search?q={quote_plus(title + ' ' + site)}&btnI=1"

        products.append({
            "id": f"{platform.lower().replace(' ', '')}-{query[:8].replace(' ', '')}-{i+1}",
            "title": title,
            "category": category,
            "price": float(price),
            "original_price": float(original),
            "discount": discount,
            "offer": f"{int(discount)}% off" if discount >= 10 else None,
            "availability": availability,
            "seller": f"{platform} Official Store",
            "rating": rating,
            "review_count": review_count,
            "image_url": None,
            "product_url": product_url,
            "relevance_score": round(priority * (rating / 5.0), 4),
            "specifications": {
                "brand": title.split()[0],
                "warranty": "1 Year",
                "_image_search_term": img_term,
            },
            "delivery_time": delivery,
        })
    return products


# ── Category detection ────────────────────────────────────────────────────────

_ELECTRONICS_KW = {
    "phone", "iphone", "samsung", "oneplus", "pixel", "redmi", "realme", "oppo",
    "vivo", "nokia", "motorola", "macbook", "notebook", "chromebook",
    "tablet", "ipad", "smartwatch", "earbuds", "airpods", "headphones",
    "earphones", "speaker", "powerbank", "power bank", "keyboard", "mouse",
    "camera", "dslr", "mirrorless", "gopro", "drone", "gaming", "console",
    "playstation", "xbox", "nintendo", "router", "modem", "ssd", "hard disk",
    "pendrive", "monitor", "projector", "printer", "scanner", "charger",
    "webcam", "microphone", "smartband", "fitness band",
    # NOTE: 'laptop' intentionally removed — 'laptop bag' must go to daily/bags
    # 'cable', 'adapter', 'hub' removed — too generic, cause false positives
}
_FASHION_KW = {
    "shirt", "tshirt", "t-shirt", "jeans", "trouser", "pant", "dress", "saree",
    "kurta", "kurti", "lehenga", "salwar", "suit", "blazer", "jacket", "coat",
    "sweater", "hoodie", "shorts", "skirt", "leggings", "top", "blouse",
    "shoes", "sneakers", "sandals", "heels", "boots", "slippers", "loafers",
    "handbag", "purse", "wallet", "belt", "sunglasses", "cap", "hat",
    "jewellery", "jewelry", "necklace", "earring", "bracelet", "ring",
    "lipstick", "foundation", "mascara", "perfume", "deodorant", "moisturizer",
    "serum", "shampoo", "conditioner", "makeup", "beauty", "skincare", "haircare",
    "fashion", "clothing", "apparel", "ethnic", "western", "formal", "casual",
}
# Short appliance words that must match as whole words only (to avoid false positives)
_APPLIANCE_WORDS = {"tv", "ac", "oven", "iron"}
_APPLIANCE_KW = {
    "refrigerator", "fridge", "washing machine", "washer", "dryer",
    "air conditioner", "split ac", "window ac", "television",
    "smart tv", "led tv", "oled", "qled", "microwave", "dishwasher",
    "water purifier", "geyser", "water heater", "vacuum cleaner",
    "air purifier", "chimney", "cooktop", "induction cooktop", "mixer grinder",
    "juicer", "toaster", "coffee maker", "sewing machine",
}
_DAILY_KW = {
    "backpack", "bag", "laptop bag", "luggage", "suitcase", "pillow", "bedsheet", "blanket",
    "curtain", "towel", "mat", "rug", "lamp", "clock", "frame", "vase",
    "candle", "decoration", "toy", "puzzle", "stationery", "pen",
    "diary", "gift", "utensil", "cookware", "pan",
    "pot", "bottle", "container", "storage", "organizer", "cleaning",
    "detergent", "soap", "sanitizer", "tissue", "grocery", "food", "snack",
    "supplement", "vitamin", "baby", "diaper", "pet", "plant",
    "garden", "tool", "hardware", "paint", "furniture", "chair", "table",
    "shelf", "rack", "mirror", "fan", "heater", "cooler",
}

# Platform priority per category: higher = more preferred (0–1)
_PLATFORM_PRIORITY = {
    "electronics": {
        "Amazon": 1.0, "Flipkart": 0.95,
        "Croma": 0.80, "Reliance Digital": 0.80,
        "Meesho": 0.30, "Myntra": 0.20, "Ajio": 0.20,
    },
    "fashion": {
        "Myntra": 1.0, "Ajio": 0.90,
        "Amazon": 0.60, "Flipkart": 0.55,
        "Meesho": 0.50, "Croma": 0.10, "Reliance Digital": 0.10,
    },
    "appliances": {
        "Reliance Digital": 1.0, "Croma": 0.95,
        "Amazon": 0.75, "Flipkart": 0.70,
        "Meesho": 0.20, "Myntra": 0.10, "Ajio": 0.10,
    },
    "daily": {
        "Meesho": 1.0, "Amazon": 0.80, "Flipkart": 0.75,
        "Myntra": 0.40, "Ajio": 0.35,
        "Croma": 0.15, "Reliance Digital": 0.15,
    },
}


def detect_category(query: str) -> str:
    """Detect product category from query keywords."""
    q = query.lower()
    words = set(q.split())

    # 1. Multi-word daily phrases checked FIRST (e.g. 'laptop bag', 'travel bag')
    for kw in _DAILY_KW:
        if " " in kw and kw in q:
            return "daily"

    # 2. Multi-word appliance phrases (e.g. 'washing machine')
    for kw in _APPLIANCE_KW:
        if " " in kw and kw in q:
            return "appliances"

    # 3. Single-word daily keywords matched as whole words (bag, backpack, etc.)
    for kw in _DAILY_KW:
        if " " not in kw and kw in words:
            return "daily"

    # 4. Electronics single-word keywords
    for kw in _ELECTRONICS_KW:
        if kw in words or kw in q:
            return "electronics"

    # 5. Single-word appliance terms
    if words & _APPLIANCE_WORDS:
        return "appliances"
    for kw in _APPLIANCE_KW:
        if kw in q:
            return "appliances"

    # 6. Fashion
    for kw in _FASHION_KW:
        if kw in words or kw in q:
            return "fashion"

    return "electronics"  # default


def platform_priority(platform: str, category: str) -> float:
    """Return priority weight (0–1) for a platform given the product category."""
    return _PLATFORM_PRIORITY.get(category, _PLATFORM_PRIORITY["electronics"]).get(platform, 0.5)


# ── URL helpers ───────────────────────────────────────────────────────────────

# Site filters used in Google "I'm Feeling Lucky" redirect to land on the exact product page
_PLATFORM_SITE = {
    "Amazon":           "site:amazon.in",
    "Flipkart":         "site:flipkart.com",
    "Meesho":           "site:meesho.com",
    "Myntra":           "site:myntra.com",
    "Ajio":             "site:ajio.com",
    "Croma":            "site:croma.com",
    "Reliance Digital": "site:reliancedigital.in",
}


def _get_product_url(platform: str, title: str) -> str:
    """
    Build a Google 'I'm Feeling Lucky' URL that redirects straight to the
    top-matching product detail page on the target platform.
    e.g. google.com/search?q=Wildcraft+Laptop+Bag+Pro+site:amazon.in&btnI=1
    """
    site = _PLATFORM_SITE.get(platform, "")
    search_term = f"{title} {site}".strip()
    encoded = quote_plus(search_term)
    return f"https://www.google.com/search?q={encoded}&btnI=1"


# ── Mock data generation ──────────────────────────────────────────────────────

# ── Per-query realistic price ranges (real Indian market prices) ─────────────
_QUERY_PRICE_MAP = {
    # iPhones
    "iphone 16":        (79999,  134900),
    "iphone 15":        (59999,   89999),
    "iphone 14":        (49999,   79999),
    "iphone 13":        (39999,   59999),
    # Samsung phones
    "samsung s24":      (74999,  109999),
    "samsung s23":      (49999,   79999),
    "samsung s22":      (39999,   69999),
    # Other phones
    "oneplus 12":       (64999,   74999),
    "oneplus 13":       (69999,   89999),
    "redmi note 13":    (14999,   24999),
    "redmi note 12":    (12999,   19999),
    "realme 12":        (12999,   19999),
    "pixel 8":          (59999,   89999),
    "pixel 7":          (49999,   69999),
    # Laptops
    "macbook air":      (99900,  149900),
    "macbook pro":      (149900, 299900),
    "hp laptop":        (35000,   80000),
    "dell laptop":      (40000,   90000),
    "lenovo laptop":    (35000,   75000),
    "asus laptop":      (35000,   80000),
    "acer laptop":      (30000,   70000),
    # Audio
    "boat earbuds":     (999,     3999),
    "boat headphones":  (1499,    4999),
    "sony headphones":  (2999,   29999),
    "jbl speaker":      (1999,   19999),
    "airpods":          (12999,   26900),
    "earbuds":          (999,     5999),
    "headphones":       (999,    29999),
    # Bags
    "laptop bag":       (599,     3499),
    "backpack":         (499,     4999),
    "school bag":       (399,     2499),
    "travel bag":       (999,     5999),
    "handbag":          (499,     4999),
    # Shoes
    "nike shoes":       (2999,   12999),
    "adidas shoes":     (2499,   10999),
    "puma shoes":       (1999,    8999),
    "sneakers":         (999,     8999),
    "shoes":            (499,     9999),
    # Watches
    "smartwatch":       (1999,   49999),
    "apple watch":      (29900,   89900),
    "samsung watch":    (14999,   49999),
    # TVs & Appliances
    "samsung tv":       (15000,  200000),
    "lg tv":            (12000,  180000),
    "refrigerator":     (12000,   80000),
    "washing machine":  (10000,   60000),
    "air conditioner":  (25000,   80000),
    "microwave":        (5000,    25000),
    # Daily
    "water bottle":     (199,     1999),
    "pillow":           (299,     2999),
    "bedsheet":         (499,     3999),
}

# Category fallback ranges when query not in map
_CATEGORY_PRICE_RANGE = {
    "electronics": (8000,  80000),
    "fashion":     (599,    8000),
    "appliances":  (10000, 120000),
    "daily":       (499,    5000),
}

# Brand prefixes used to build realistic product titles
_BRAND_PREFIXES = {
    "electronics": ["Samsung", "Sony", "HP", "Dell", "Apple", "OnePlus", "Boat", "JBL"],
    "fashion":     ["Nike", "Adidas", "Puma", "Levi's", "H&M", "Zara", "Allen Solly"],
    "appliances":  ["LG", "Samsung", "Whirlpool", "Bosch", "Haier", "Voltas", "IFB"],
    "daily":       ["Wildcraft", "Skybags", "American Tourister", "Safari", "VIP", "Aristocrat"],
}

# Descriptive suffixes to make titles feel realistic
_TITLE_SUFFIXES = [
    "Pro", "Plus", "Lite", "Max", "Ultra", "Premium", "Classic",
    "Edition", "Series", "Collection", "Special",
]


def _stable_seed(platform: str, query: str, index: int) -> int:
    """Deterministic seed so same query always returns same prices."""
    return sum(ord(c) for c in (platform + query).lower()) + index * 31


def _get_price_range(query: str, category: str):
    """Return (min, max) — query-specific first, then category fallback."""
    q = query.lower().strip()
    if q in _QUERY_PRICE_MAP:
        return _QUERY_PRICE_MAP[q]
    for key, rng in _QUERY_PRICE_MAP.items():
        if key in q or q in key:
            return rng
    return _CATEGORY_PRICE_RANGE.get(category, (500, 50000))


def _realistic_price(query: str, category: str, platform: str, index: int) -> float:
    """Stable realistic price within the correct range with small per-platform variation."""
    lo, hi = _get_price_range(query, category)
    seed = _stable_seed(platform, query, index)
    random.seed(seed)
    # Use lower 60% of range so prices feel like real market listings, not outliers
    mid = lo + (hi - lo) * 0.6
    base = random.uniform(lo, mid)
    variation = random.uniform(0.95, 1.05)  # ±5% per platform
    random.seed()
    return max(lo, round(base * variation / 10) * 10)  # round to nearest ₹10


def _build_title(query: str, category: str, platform: str, index: int) -> str:
    """
    Build a product title that ALWAYS contains the exact search query.
    Format: <Brand> <query> <Suffix>
    This guarantees search results are always relevant to the query.
    """
    seed = _stable_seed(platform, query, index)
    random.seed(seed)
    brands = _BRAND_PREFIXES.get(category, ["Generic"])
    brand = brands[index % len(brands)]
    suffix = _TITLE_SUFFIXES[index % len(_TITLE_SUFFIXES)]
    random.seed()
    return f"{brand} {query.title()} {suffix}"





# ── Adapters ──────────────────────────────────────────────────────────────────────────────────

class AmazonAdapter(BaseAdapter):
    platform_name = "Amazon"

    async def search(self, query: str, category: str = "electronics", **kwargs) -> List[ProductSchema]:
        # Try real RapidAPI first; fall back to realistic mock
        from app.agents.product_search.real_api import fetch_amazon_products
        real = await fetch_amazon_products(query, max_results=6)
        if real:
            for p in real:
                p["category"] = p["category"] or category
            return [self._normalize(p) for p in real]
        await asyncio.sleep(0.1)
        return [self._normalize(p) for p in _mock_products("Amazon", query, 6, category)]


class FlipkartAdapter(BaseAdapter):
    platform_name = "Flipkart"

    async def search(self, query: str, category: str = "electronics", **kwargs) -> List[ProductSchema]:
        await asyncio.sleep(0.1)
        return [self._normalize(p) for p in _mock_products("Flipkart", query, 5, category)]


class MeeshoAdapter(BaseAdapter):
    platform_name = "Meesho"

    async def search(self, query: str, category: str = "electronics", **kwargs) -> List[ProductSchema]:
        await asyncio.sleep(0.1)
        return [self._normalize(p) for p in _mock_products("Meesho", query, 4, category)]


class MyntraAdapter(BaseAdapter):
    platform_name = "Myntra"

    async def search(self, query: str, category: str = "electronics", **kwargs) -> List[ProductSchema]:
        await asyncio.sleep(0.1)
        return [self._normalize(p) for p in _mock_products("Myntra", query, 4, category)]


class AjioAdapter(BaseAdapter):
    platform_name = "Ajio"

    async def search(self, query: str, category: str = "electronics", **kwargs) -> List[ProductSchema]:
        await asyncio.sleep(0.1)
        return [self._normalize(p) for p in _mock_products("Ajio", query, 3, category)]


class CromaAdapter(BaseAdapter):
    platform_name = "Croma"

    async def search(self, query: str, category: str = "electronics", **kwargs) -> List[ProductSchema]:
        await asyncio.sleep(0.1)
        return [self._normalize(p) for p in _mock_products("Croma", query, 4, category)]


class RelianceDigitalAdapter(BaseAdapter):
    platform_name = "Reliance Digital"

    async def search(self, query: str, category: str = "electronics", **kwargs) -> List[ProductSchema]:
        await asyncio.sleep(0.1)
        return [self._normalize(p) for p in _mock_products("Reliance Digital", query, 4, category)]
