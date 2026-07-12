"""
Real product data fetcher using RapidAPI.
Uses "Real-Time Amazon Data" API from RapidAPI.
Sign up free at https://rapidapi.com/letscrape-6bRBa3QguO5/api/real-time-amazon-data

Set RAPIDAPI_KEY in your .env file to enable real prices.
Falls back to mock data if key is missing or API fails.
"""
import httpx
from typing import List, Optional
from loguru import logger
from app.config.settings import settings


RAPIDAPI_HOST = "real-time-amazon-data.p.rapidapi.com"


async def fetch_amazon_products(query: str, max_results: int = 6) -> Optional[List[dict]]:
    """
    Fetch real Amazon India products via RapidAPI.
    Returns list of normalized product dicts, or None if unavailable.
    """
    if not settings.RAPIDAPI_KEY or settings.RAPIDAPI_KEY == "your_rapidapi_key_here":
        return None

    url = "https://real-time-amazon-data.p.rapidapi.com/search"
    headers = {
        "X-RapidAPI-Key": settings.RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST,
    }
    params = {
        "query": query,
        "page": "1",
        "country": "IN",
        "sort_by": "RELEVANCE",
        "product_condition": "ALL",
    }

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(url, headers=headers, params=params)
            resp.raise_for_status()
            data = resp.json()

        items = data.get("data", {}).get("products", [])
        if not items:
            return None

        results = []
        for item in items[:max_results]:
            # Parse price — RapidAPI returns strings like "₹1,299" or "$19.99"
            price = _parse_price(item.get("product_price") or item.get("product_original_price"))
            original = _parse_price(item.get("product_original_price")) or price
            if not price:
                continue

            discount = 0.0
            if original and original > price:
                discount = round((original - price) / original * 100, 1)

            rating_raw = item.get("product_star_rating") or "0"
            try:
                rating = float(str(rating_raw).replace(",", "."))
            except Exception:
                rating = 0.0

            review_raw = item.get("product_num_ratings") or "0"
            try:
                review_count = int(str(review_raw).replace(",", "").replace(".", ""))
            except Exception:
                review_count = 0

            product_url = item.get("product_url") or f"https://www.amazon.in/s?k={query}"
            if product_url and not product_url.startswith("http"):
                product_url = "https://www.amazon.in" + product_url

            results.append({
                "id":             item.get("asin", f"amz-{len(results)+1}"),
                "title":          item.get("product_title", query),
                "category":       None,
                "price":          price,
                "original_price": original,
                "discount":       discount,
                "offer":          f"{int(discount)}% off" if discount >= 5 else None,
                "availability":   item.get("is_prime", True),
                "seller":         "Amazon India",
                "rating":         rating if rating > 0 else None,
                "review_count":   review_count if review_count > 0 else None,
                "image_url":      item.get("product_photo"),
                "product_url":    product_url,
                "relevance_score": 1.0,
                "specifications": {
                    "brand": item.get("product_title", "").split()[0] if item.get("product_title") else "Unknown",
                    "asin":  item.get("asin", ""),
                },
                "delivery_time":  "1-2 days" if item.get("is_prime") else "3-5 days",
            })

        logger.info(f"RapidAPI: fetched {len(results)} real Amazon products for '{query}'")
        return results if results else None

    except httpx.TimeoutException:
        logger.warning(f"RapidAPI timeout for query '{query}'")
        return None
    except Exception as e:
        logger.warning(f"RapidAPI error for '{query}': {e}")
        return None


def _parse_price(raw) -> Optional[float]:
    """Parse price string like '₹1,299' or '1299.00' to float."""
    if not raw:
        return None
    try:
        cleaned = str(raw).replace("₹", "").replace("$", "").replace(",", "").strip()
        return float(cleaned)
    except Exception:
        return None
