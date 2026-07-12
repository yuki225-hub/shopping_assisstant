from typing import List, Optional, Dict
from loguru import logger
from app.schemas.product import ProductSchema, PriceComparisonSchema


class PriceComparisonAgent:
    """Agent 2: Compares the SAME product across platforms."""

    def compare(self, products: List[ProductSchema]) -> PriceComparisonSchema:
        priced = [p for p in products if p.price is not None]

        if not priced:
            return PriceComparisonSchema(
                lowest_price=None,
                highest_price=None,
                average_price=None,
                best_value_product=None,
                cheapest_product=None,
                premium_product=None,
                comparison_table=[],
            )

        prices = [p.price for p in priced]
        lowest = min(prices)
        highest = max(prices)
        average = round(sum(prices) / len(prices), 2)

        cheapest = min(priced, key=lambda p: p.price)
        premium = max(priced, key=lambda p: p.price)

        def value_score(p: ProductSchema) -> float:
            rating = p.rating or 3.0
            discount = p.discount or 0
            return (rating * (1 + discount / 100)) / (p.price or 1)

        best_value = max(priced, key=value_score)

        # Group by platform — one row per platform showing that platform's best price
        # for the searched product (same query = same product across platforms)
        platform_best: Dict[str, ProductSchema] = {}
        for p in priced:
            existing = platform_best.get(p.platform)
            if existing is None or (p.price or 0) < (existing.price or 0):
                platform_best[p.platform] = p

        comparison_table = [
            {
                "platform": p.platform,
                "title": p.title[:60],
                "price": p.price,
                "original_price": p.original_price,
                "discount": p.discount,
                "rating": p.rating,
                "review_count": p.review_count,
                "availability": p.availability,
                "delivery_time": p.delivery_time,
                "product_url": p.product_url,
                "value_score": round(value_score(p), 4),
            }
            for p in sorted(platform_best.values(), key=lambda p: p.price or 0)
        ]

        logger.info(f"PriceComparisonAgent: lowest={lowest}, highest={highest}, avg={average}, platforms={len(platform_best)}")
        return PriceComparisonSchema(
            lowest_price=lowest,
            highest_price=highest,
            average_price=average,
            best_value_product=best_value.title,
            cheapest_product=cheapest.title,
            premium_product=premium.title,
            comparison_table=comparison_table,
        )
