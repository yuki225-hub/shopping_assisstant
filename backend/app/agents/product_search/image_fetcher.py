"""
Fetches real product images using the Openverse API (api.openverse.org).
- Zero API keys required, zero signup
- Returns actual product photos matching the search query
- One fetch per unique query, cached for the server session
- Falls back to Google CSE if configured
"""
import asyncio
import httpx
from typing import Optional
from urllib.parse import quote_plus
from loguru import logger
from app.config.settings import settings

# Cache: query_key -> image_url
_image_cache: dict = {}

_PLATFORM_SEARCH_URL = {
    "Amazon":           "https://www.google.com/search?q={q}+site:amazon.in&btnI=1",
    "Flipkart":         "https://www.google.com/search?q={q}+site:flipkart.com&btnI=1",
    "Meesho":           "https://www.google.com/search?q={q}+site:meesho.com&btnI=1",
    "Myntra":           "https://www.google.com/search?q={q}+site:myntra.com&btnI=1",
    "Ajio":             "https://www.google.com/search?q={q}+site:ajio.com&btnI=1",
    "Croma":            "https://www.google.com/search?q={q}+site:croma.com&btnI=1",
    "Reliance Digital": "https://www.google.com/search?q={q}+site:reliancedigital.in&btnI=1",
}


def _platform_url(platform: str, title: str) -> str:
    encoded = quote_plus(title)
    template = _PLATFORM_SEARCH_URL.get(platform, "https://www.google.com/search?q={q}+buy+online")
    return template.format(q=encoded)


async def _openverse_image(query: str) -> Optional[str]:
    """
    Fetch a real product image from Openverse (api.openverse.org).
    Free, no API key, returns CC-licensed real photos for any product query.
    """
    try:
        async with httpx.AsyncClient(timeout=6.0, follow_redirects=True) as client:
            r = await client.get(
                "https://api.openverse.org/v1/images/",
                params={
                    "q": query,
                    "page_size": 5,
                    "license_type": "commercial,modification",
                },
                headers={"User-Agent": "ShopMind/1.0"},
            )
            if r.status_code == 200:
                items = r.json().get("results", [])
                # Pick first item that has a direct image URL
                for item in items:
                    # Prefer thumbnail (served from Openverse CDN, no CORS issues)
                    # over url (often Flickr which blocks cross-origin img loads)
                    url = item.get("thumbnail") or item.get("url")
                    if url and url.startswith("http"):
                        return url
    except Exception as e:
        logger.warning(f"Openverse error for '{query}': {e}")
    return None


async def _google_cse_image(query: str) -> Optional[str]:
    """Uses Google Custom Search image API if keys are configured."""
    if not (settings.GOOGLE_API_KEY and settings.GOOGLE_CSE_ID):
        return None
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(
                "https://www.googleapis.com/customsearch/v1",
                params={
                    "key": settings.GOOGLE_API_KEY,
                    "cx": settings.GOOGLE_CSE_ID,
                    "q": f"{query} product",
                    "searchType": "image",
                    "num": 1,
                    "imgSize": "MEDIUM",
                    "safe": "active",
                },
            )
            items = r.json().get("items", [])
            if items:
                return items[0]["link"]
    except Exception:
        pass
    return None


async def _fetch_image(query: str) -> Optional[str]:
    """
    Fetch best available real product image for query.
    Openverse first (free, no key), Google CSE fallback.
    Cached so same query never hits API twice per server session.
    """
    key = query.lower().strip()
    if key in _image_cache:
        return _image_cache[key]

    img = await _openverse_image(query)
    if not img:
        img = await _google_cse_image(query)

    _image_cache[key] = img
    logger.info(f"ImageFetcher: '{query}' -> {'OK: ' + img[:60] if img else 'not found'}")
    return img


def _brand_query(title: str, query: str) -> str:
    """
    Extract a specific image search term from the product title.
    Uses 'Brand + query' so Nike shoes, Adidas shoes, Puma shoes
    each get their own distinct image instead of all sharing one.
    e.g. title='Nike Shoes Pro' query='shoes' -> 'Nike shoes'
         title='Samsung Laptop Plus' query='laptop' -> 'Samsung laptop'
    """
    words = title.split()
    brand = words[0] if words else ""
    # If brand is a known generic suffix word, fall back to full query
    generic = {"the", "a", "an", "new", "best", "top", "buy"}
    if brand.lower() in generic:
        return query
    return f"{brand} {query}"


async def enrich_products(products: list, query: str) -> list:
    """
    Sets image_url and product_url on every product dict.

    Image: fetches one image per unique brand+query combination so that
    'Nike shoes', 'Adidas shoes', 'Puma shoes' each show a different image.
    Results are cached so repeated brand queries cost zero API calls.

    URL: each product gets a Google I'm Feeling Lucky URL scoped to its
    exact title + platform site filter.
    """
    if not products:
        return products

    # Build unique brand-query keys for all products
    unique_bq = list({
        (p.get("specifications") or {}).get("_image_search_term") or _brand_query(p.get("title", query), query)
        for p in products
    })

    # Fetch all brand images concurrently
    fetched = await asyncio.gather(*[_fetch_image(bq) for bq in unique_bq])
    bq_image = dict(zip(unique_bq, fetched))

    # Fallback: query-level image if a brand fetch returned nothing
    query_image = await _fetch_image(query)

    for product in products:
        platform = product.get("platform", "")
        title = product.get("title", query)
        # Use explicit image_search_term if stored in specifications, else derive from title
        specs = product.get("specifications") or {}
        explicit_term = specs.get("_image_search_term")
        bq = explicit_term or _brand_query(title, query)
        img = bq_image.get(bq) or query_image
        if img:
            product["image_url"] = img
        product["product_url"] = _platform_url(platform, title)

    return products
