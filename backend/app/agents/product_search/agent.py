import asyncio
from typing import List, Optional
from loguru import logger
from app.schemas.product import ProductSchema
from app.agents.product_search.adapters import (
    AmazonAdapter, FlipkartAdapter, MeeshoAdapter,
    MyntraAdapter, AjioAdapter, CromaAdapter, RelianceDigitalAdapter,
    detect_category,
)
from app.agents.product_search.image_fetcher import enrich_products

ALL_ADAPTERS = {
    "amazon": AmazonAdapter(),
    "flipkart": FlipkartAdapter(),
    "meesho": MeeshoAdapter(),
    "myntra": MyntraAdapter(),
    "ajio": AjioAdapter(),
    "croma": CromaAdapter(),
    "reliance digital": RelianceDigitalAdapter(),
}


class ProductSearchAgent:
    """Agent 1: Searches products across multiple platforms concurrently."""

    async def search(
        self,
        query: str,
        platforms: Optional[List[str]] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_rating: Optional[float] = None,
    ) -> List[ProductSchema]:
        category = detect_category(query)
        logger.info(f"ProductSearchAgent detected category='{category}' for query='{query}'")

        selected = {
            k: v for k, v in ALL_ADAPTERS.items()
            if not platforms or k in [p.lower() for p in platforms]
        }

        tasks = [adapter.search(query, category=category) for adapter in selected.values()]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        products: List[ProductSchema] = []
        for platform, result in zip(selected.keys(), results):
            if isinstance(result, Exception):
                logger.warning(f"Adapter {platform} failed: {result}")
                continue
            products.extend(result)

        # Apply filters
        if min_price is not None:
            products = [p for p in products if p.price and p.price >= min_price]
        if max_price is not None:
            products = [p for p in products if p.price and p.price <= max_price]
        if min_rating is not None:
            products = [p for p in products if p.rating and p.rating >= min_rating]

        # Enrich with real images and exact product URLs (one API call per platform)
        raw = [p.model_dump() for p in products]
        enriched = await enrich_products(raw, query)
        products = [ProductSchema(**p) for p in enriched]

        logger.info(f"ProductSearchAgent found {len(products)} products for '{query}' (category={category})")
        return products
