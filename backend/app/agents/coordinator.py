from typing import Optional, List, Dict, Any
from loguru import logger
from app.schemas.product import SearchResponse, SearchRequest
from app.agents.product_search.agent import ProductSearchAgent
from app.agents.price_compare.agent import PriceComparisonAgent
from app.agents.review_analysis.agent import ReviewAnalysisAgent
from app.agents.recommendation.agent import RecommendationAgent


class CoordinatorAgent:
    """
    Orchestrates all specialized agents to produce a complete search response.
    Flow: Search → Price Compare → Review Analysis → Recommendation
    """

    def __init__(self):
        self.search_agent = ProductSearchAgent()
        self.price_agent = PriceComparisonAgent()
        self.review_agent = ReviewAnalysisAgent()
        self.recommendation_agent = RecommendationAgent()

    async def process(
        self,
        request: SearchRequest,
        user_preferences: Optional[Dict[str, Any]] = None,
    ) -> SearchResponse:
        logger.info(f"CoordinatorAgent processing query: '{request.query}'")

        # Step 1: Search products
        products = await self.search_agent.search(
            query=request.query,
            platforms=request.platforms,
            min_price=request.min_price,
            max_price=request.max_price,
            min_rating=request.min_rating,
        )

        # Step 2: Sort products
        products = self._sort_products(products, request.sort_by)

        # Step 3: Price comparison (on all products)
        total = len(products)
        price_comparison = self.price_agent.compare(products)

        # Step 4: Review analysis
        review_analysis = self.review_agent.analyze(products)

        # Step 5: Recommendation
        recommendation = self.recommendation_agent.recommend(
            products, price_comparison, review_analysis, user_preferences,
            query=request.query,
        )

        # Return ALL products — service will paginate after persisting IDs
        logger.info(f"CoordinatorAgent completed: {total} products, score={recommendation.score}")
        return SearchResponse(
            query=request.query,
            total_results=total,
            products=products,
            price_comparison=price_comparison,
            review_analysis=review_analysis,
            recommendation=recommendation,
        )

    def _sort_products(self, products, sort_by: Optional[str]):
        if sort_by == "price_asc":
            return sorted(products, key=lambda p: p.price or float("inf"))
        elif sort_by == "price_desc":
            return sorted(products, key=lambda p: p.price or 0, reverse=True)
        elif sort_by == "rating":
            return sorted(products, key=lambda p: p.rating or 0, reverse=True)
        elif sort_by == "discount":
            return sorted(products, key=lambda p: p.discount or 0, reverse=True)
        return products  # relevance (default)
