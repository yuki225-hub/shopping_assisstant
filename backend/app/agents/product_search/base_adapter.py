from abc import ABC, abstractmethod
from typing import List
from app.schemas.product import ProductSchema


class BaseAdapter(ABC):
    """Base adapter that all platform adapters must implement."""

    platform_name: str = ""

    @abstractmethod
    async def search(self, query: str, **kwargs) -> List[ProductSchema]:
        """Search products on the platform and return normalized ProductSchema list."""
        pass

    def _normalize(self, raw: dict) -> ProductSchema:
        """Helper to build ProductSchema from raw dict."""
        return ProductSchema(
            platform=self.platform_name,
            external_id=raw.get("id"),
            title=raw.get("title", ""),
            category=raw.get("category"),
            price=raw.get("price"),
            original_price=raw.get("original_price"),
            discount=raw.get("discount"),
            offer=raw.get("offer"),
            availability=raw.get("availability", True),
            seller=raw.get("seller"),
            rating=raw.get("rating"),
            review_count=raw.get("review_count"),
            image_url=raw.get("image_url"),
            product_url=raw.get("product_url"),
            relevance_score=raw.get("relevance_score"),
            specifications=raw.get("specifications", {}),
            delivery_time=raw.get("delivery_time"),
        )
