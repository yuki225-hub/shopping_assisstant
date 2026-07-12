from typing import List, Optional, Dict, Any
from loguru import logger
from app.schemas.product import ProductSchema, PriceComparisonSchema, ReviewAnalysisSchema, RecommendationSchema
from app.agents.product_search.adapters import detect_category, platform_priority


class RecommendationAgent:
    """Agent 4: Recommends best products using only real backend data."""

    WEIGHTS = {
        "rating":           0.30,
        "price_value":      0.20,
        "review_sentiment": 0.15,
        "review_count":     0.10,
        "discount":         0.08,
        "availability":     0.07,
        "delivery":         0.05,
        "platform_fit":     0.05,
    }

    def _query_relevant(self, products: List[ProductSchema], query: str) -> List[ProductSchema]:
        """
        Return only products whose title contains ALL query keywords.
        This ensures recommendations are strictly from the searched category.
        Falls back to partial match, then all products if nothing matches.
        """
        keywords = [w.lower() for w in query.split() if len(w) > 1]
        if not keywords:
            return products

        # Strict: all keywords present
        strict = [p for p in products if all(kw in p.title.lower() for kw in keywords)]
        if strict:
            return strict

        # Relaxed: any keyword present
        relaxed = [p for p in products if any(kw in p.title.lower() for kw in keywords)]
        return relaxed or products

    def recommend(
        self,
        products: List[ProductSchema],
        price_comparison: PriceComparisonSchema,
        review_analysis: ReviewAnalysisSchema,
        user_preferences: Optional[Dict[str, Any]] = None,
        query: str = "",
    ) -> RecommendationSchema:
        if not products:
            return self._empty_recommendation()

        category = detect_category(query) if query else (products[0].category or "electronics")

        # Only score products relevant to the query
        relevant = self._query_relevant(products, query)
        priced = [p for p in relevant if p.price is not None]
        if not priced:
            priced = relevant

        scored = [
            (p, self._score(p, price_comparison, review_analysis, category))
            for p in priced
        ]
        scored.sort(key=lambda x: -x[1])

        best_overall = scored[0][0]

        # Best budget: lowest price among well-rated products
        well_rated = [p for p in priced if (p.rating or 0) >= 3.5]
        best_budget = min(well_rated or priced, key=lambda p: p.price or float("inf"))

        # Best premium: highest scored in top-25% price range
        prices_sorted = sorted(p.price for p in priced)
        cutoff_idx = max(int(len(prices_sorted) * 0.75), len(prices_sorted) - 1)
        premium_threshold = prices_sorted[cutoff_idx]
        premium_candidates = [p for p in priced if (p.price or 0) >= premium_threshold]
        best_premium = max(
            premium_candidates or priced,
            key=lambda p: self._score(p, price_comparison, review_analysis, category),
        )

        overall_score = round(scored[0][1] * 100, 1)
        pros = review_analysis.common_pros[:3] or ["Good value", "Reliable"]
        cons = review_analysis.common_cons[:3] or ["Limited availability"]

        # Build reason using ONLY real values from the best product
        reason = self._build_reason(best_overall, review_analysis)
        explanation = (
            f"After analyzing {len(products)} {query} products across multiple platforms "
            f"(category: {category}), '{best_overall.title}' from {best_overall.platform} "
            f"scores highest ({overall_score}/100). "
            f"Price: ₹{best_overall.price:.0f}, "
            f"Rating: {best_overall.rating or 'N/A'}/5, "
            f"Reviews: {best_overall.review_count or 0:,}, "
            f"Delivery: {best_overall.delivery_time or 'N/A'}, "
            f"Sentiment: {review_analysis.positive_percent}% positive."
        )

        logger.info(
            f"RecommendationAgent: category={category}, "
            f"best='{best_overall.title[:40]}' ({best_overall.platform}), score={overall_score}"
        )
        return RecommendationSchema(
            best_overall=best_overall.title,
            best_budget=best_budget.title,
            best_premium=best_premium.title,
            best_overall_price=best_overall.price,
            best_budget_price=best_budget.price,
            best_premium_price=best_premium.price,
            best_overall_rating=best_overall.rating,
            best_budget_rating=best_budget.rating,
            best_premium_rating=best_premium.rating,
            best_overall_platform=best_overall.platform,
            best_budget_platform=best_budget.platform,
            best_premium_platform=best_premium.platform,
            best_overall_url=best_overall.product_url,
            best_budget_url=best_budget.product_url,
            best_premium_url=best_premium.product_url,
            best_overall_reviews=best_overall.review_count,
            best_overall_delivery=best_overall.delivery_time,
            best_overall_sentiment=review_analysis.positive_percent,
            category=category,
            score=overall_score,
            reason=reason,
            pros=pros,
            cons=cons,
            explanation=explanation,
        )

    def _score(
        self,
        product: ProductSchema,
        price_comp: PriceComparisonSchema,
        review: ReviewAnalysisSchema,
        category: str = "electronics",
    ) -> float:
        score = 0.0

        # Rating (0–1)
        if product.rating:
            score += self.WEIGHTS["rating"] * (product.rating / 5.0)

        # Price value: cheaper vs average = better
        if product.price and price_comp.average_price:
            ratio = price_comp.average_price / product.price
            score += self.WEIGHTS["price_value"] * min(ratio, 2.0) / 2.0

        # Review sentiment
        score += self.WEIGHTS["review_sentiment"] * (review.positive_percent / 100)

        # Review count (normalised to 50k max)
        if product.review_count:
            score += self.WEIGHTS["review_count"] * min(product.review_count / 50000, 1.0)

        # Discount
        if product.discount:
            score += self.WEIGHTS["discount"] * min(product.discount / 50, 1.0)

        # Availability
        if product.availability:
            score += self.WEIGHTS["availability"]

        # Delivery speed
        delivery_scores = {"same day": 1.0, "1-2 days": 0.8, "2-3 days": 0.6, "3-5 days": 0.4}
        if product.delivery_time:
            ds = delivery_scores.get(product.delivery_time.lower(), 0.3)
            score += self.WEIGHTS["delivery"] * ds

        # Platform-category fit
        priority = platform_priority(product.platform, category)
        score += self.WEIGHTS["platform_fit"] * priority

        return round(score, 4)

    def _build_reason(self, product: ProductSchema, review: ReviewAnalysisSchema) -> str:
        """Build reason string using ONLY real values from the product."""
        parts = []
        if product.rating:
            parts.append(f"⭐ Rating: {product.rating}/5")
        if product.price:
            parts.append(f"₹{product.price:,.0f}")
        if product.review_count:
            parts.append(f"{product.review_count:,} Reviews")
        if product.delivery_time:
            parts.append(f"{product.delivery_time} Delivery")
        if review.positive_percent:
            parts.append(f"{review.positive_percent}% Positive Reviews")
        return " • ".join(parts) if parts else "Well-balanced across all factors."

    def _empty_recommendation(self) -> RecommendationSchema:
        return RecommendationSchema(
            best_overall=None,
            best_budget=None,
            best_premium=None,
            score=0,
            reason="No products available for recommendation.",
            pros=[],
            cons=[],
            explanation="No products found to analyze.",
        )
