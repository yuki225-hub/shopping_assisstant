from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from app.models.product import Product, Comparison
from app.models.search_history import Wishlist, SearchHistory
from app.repositories.base import BaseRepository


class ProductRepository(BaseRepository[Product]):
    def __init__(self, db: AsyncSession):
        super().__init__(Product, db)

    async def get_by_query(self, query: str, skip: int = 0, limit: int = 20) -> List[Product]:
        result = await self.db.execute(
            select(Product)
            .where(Product.search_query.ilike(f"%{query}%"))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_ids(self, ids: List[int]) -> List[Product]:
        result = await self.db.execute(select(Product).where(Product.id.in_(ids)))
        return list(result.scalars().all())


class WishlistRepository(BaseRepository[Wishlist]):
    def __init__(self, db: AsyncSession):
        super().__init__(Wishlist, db)

    async def get_user_wishlist(self, user_id: int) -> List[Wishlist]:
        result = await self.db.execute(
            select(Wishlist)
            .options(selectinload(Wishlist.product))
            .where(Wishlist.user_id == user_id)
        )
        return list(result.scalars().all())

    async def get_user_wishlist_item(self, user_id: int, product_id: int) -> Optional[Wishlist]:
        result = await self.db.execute(
            select(Wishlist).where(
                and_(Wishlist.user_id == user_id, Wishlist.product_id == product_id)
            )
        )
        return result.scalar_one_or_none()

    async def get_by_id_with_product(self, wishlist_id: int) -> Optional[Wishlist]:
        result = await self.db.execute(
            select(Wishlist)
            .options(selectinload(Wishlist.product))
            .where(Wishlist.id == wishlist_id)
        )
        return result.scalar_one_or_none()


class SearchHistoryRepository(BaseRepository[SearchHistory]):
    def __init__(self, db: AsyncSession):
        super().__init__(SearchHistory, db)

    async def get_user_history(self, user_id: int, limit: int = 20) -> List[SearchHistory]:
        result = await self.db.execute(
            select(SearchHistory)
            .where(SearchHistory.user_id == user_id)
            .order_by(SearchHistory.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def delete_user_history(self, user_id: int) -> None:
        from sqlalchemy import delete
        await self.db.execute(delete(SearchHistory).where(SearchHistory.user_id == user_id))
        await self.db.flush()
