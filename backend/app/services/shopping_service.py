from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.agents.coordinator import CoordinatorAgent
from app.models.product import Product, Comparison
from app.models.search_history import Wishlist, SearchHistory
from app.repositories.product_repository import ProductRepository, WishlistRepository, SearchHistoryRepository
from app.schemas.product import (
    SearchRequest, SearchResponse, WishlistCreate, WishlistResponse,
    PriceComparisonSchema, ReviewAnalysisSchema, RecommendationSchema,
    AnalyzeReviewsRequest, CompareRequest,
)
from app.agents.price_compare.agent import PriceComparisonAgent
from app.agents.review_analysis.agent import ReviewAnalysisAgent
from app.agents.recommendation.agent import RecommendationAgent
from app.core.exceptions import NotFoundError, ConflictError


class ShoppingService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.product_repo = ProductRepository(db)
        self.wishlist_repo = WishlistRepository(db)
        self.history_repo = SearchHistoryRepository(db)
        self.coordinator = CoordinatorAgent()

    async def search(self, request: SearchRequest, user_id: Optional[int] = None) -> SearchResponse:
        response = await self.coordinator.process(
            request,
            user_preferences=None,
        )

        # Persist all products to DB first (assigns IDs), then paginate
        for p in response.products:
            product = Product(
                platform=p.platform,
                external_id=p.external_id,
                title=p.title,
                category=p.category,
                price=p.price,
                original_price=p.original_price,
                discount=p.discount,
                offer=p.offer,
                availability=p.availability,
                seller=p.seller,
                rating=p.rating,
                review_count=p.review_count,
                image_url=p.image_url,
                product_url=p.product_url,
                relevance_score=p.relevance_score,
                specifications=p.specifications,
                delivery_time=p.delivery_time,
                search_query=request.query,
            )
            saved = await self.product_repo.create(product)
            p.id = saved.id

        # Re-apply pagination AFTER IDs are assigned
        total = response.total_results
        start = (request.page - 1) * request.page_size
        response.products = response.products[start: start + request.page_size]

        # Save search history
        if user_id:
            history = SearchHistory(
                user_id=user_id,
                query=request.query,
                result_count=response.total_results,
            )
            await self.history_repo.create(history)

        return response

    async def get_product(self, product_id: int) -> Product:
        product = await self.product_repo.get_by_id(product_id)
        if not product:
            raise NotFoundError("Product")
        return product

    async def compare_products(self, request: CompareRequest) -> dict:
        products_db = await self.product_repo.get_by_ids(request.product_ids)
        if not products_db:
            raise NotFoundError("Products")

        from app.schemas.product import ProductSchema
        products = [ProductSchema.model_validate(p) for p in products_db]

        price_agent = PriceComparisonAgent()
        review_agent = ReviewAnalysisAgent()
        rec_agent = RecommendationAgent()

        price_comp = price_agent.compare(products)
        review_analysis = review_agent.analyze(products)
        recommendation = rec_agent.recommend(products, price_comp, review_analysis)

        return {
            "products": [p.model_dump() for p in products],
            "price_comparison": price_comp.model_dump(),
            "review_analysis": review_analysis.model_dump(),
            "recommendation": recommendation.model_dump(),
        }

    async def analyze_reviews(self, request: AnalyzeReviewsRequest) -> ReviewAnalysisSchema:
        agent = ReviewAnalysisAgent()
        return agent.analyze([], extra_reviews=request.reviews)

    # Wishlist
    async def get_wishlist(self, user_id: int) -> List[Wishlist]:
        return await self.wishlist_repo.get_user_wishlist(user_id)

    async def add_to_wishlist(self, user_id: int, data: WishlistCreate) -> Wishlist:
        existing = await self.wishlist_repo.get_user_wishlist_item(user_id, data.product_id)
        if existing:
            raise ConflictError("Product already in wishlist")

        product = await self.product_repo.get_by_id(data.product_id)
        if not product:
            raise NotFoundError("Product")

        item = Wishlist(user_id=user_id, product_id=data.product_id, note=data.note)
        created = await self.wishlist_repo.create(item)
        return await self.wishlist_repo.get_by_id_with_product(created.id)

    async def remove_from_wishlist(self, user_id: int, wishlist_id: int) -> None:
        item = await self.wishlist_repo.get_by_id(wishlist_id)
        if not item or item.user_id != user_id:
            raise NotFoundError("Wishlist item")
        await self.wishlist_repo.delete(item)

    # Search History
    async def get_history(self, user_id: int) -> List[SearchHistory]:
        return await self.history_repo.get_user_history(user_id)

    async def clear_history(self, user_id: int) -> None:
        await self.history_repo.delete_user_history(user_id)
