from fastapi import APIRouter, Depends, Query, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.services.shopping_service import ShoppingService
from app.core.dependencies import get_current_user
from app.core.security import decode_token
from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.schemas.product import (
    SearchRequest, SearchResponse, WishlistCreate, WishlistResponse,
    SearchHistoryResponse, CompareRequest, AnalyzeReviewsRequest, ProductSchema,
)

router = APIRouter(tags=["Shopping"])
_optional_bearer = HTTPBearer(auto_error=False)


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_optional_bearer),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    if not credentials:
        return None
    payload = decode_token(credentials.credentials)
    if not payload or payload.get("type") != "access":
        return None
    repo = UserRepository(db)
    return await repo.get_by_id(int(payload.get("sub", 0)))


@router.get("/search", response_model=SearchResponse)
async def search_products(
    q: str = Query(..., min_length=1, description="Search query"),
    platforms: Optional[str] = Query(None, description="Comma-separated platforms"),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    min_rating: Optional[float] = Query(None, ge=0, le=5),
    sort_by: Optional[str] = Query("relevance", enum=["relevance", "price_asc", "price_desc", "rating", "discount"]),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    request = SearchRequest(
        query=q,
        platforms=platforms.split(",") if platforms else None,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating,
        sort_by=sort_by,
        page=page,
        page_size=page_size,
    )
    service = ShoppingService(db)
    return await service.search(request, user_id=current_user.id if current_user else None)


@router.get("/product/{product_id}", response_model=ProductSchema)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    service = ShoppingService(db)
    return await service.get_product(product_id)


@router.post("/compare")
async def compare_products(request: CompareRequest, db: AsyncSession = Depends(get_db)):
    service = ShoppingService(db)
    return await service.compare_products(request)


@router.post("/recommend")
async def recommend(request: CompareRequest, db: AsyncSession = Depends(get_db)):
    service = ShoppingService(db)
    return await service.compare_products(request)


@router.post("/analyze-reviews")
async def analyze_reviews(request: AnalyzeReviewsRequest, db: AsyncSession = Depends(get_db)):
    service = ShoppingService(db)
    return await service.analyze_reviews(request)


# Wishlist
@router.get("/wishlist", response_model=List[WishlistResponse])
async def get_wishlist(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ShoppingService(db)
    return await service.get_wishlist(current_user.id)


@router.post("/wishlist", response_model=WishlistResponse, status_code=status.HTTP_201_CREATED)
async def add_to_wishlist(
    data: WishlistCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ShoppingService(db)
    return await service.add_to_wishlist(current_user.id, data)


@router.delete("/wishlist/{wishlist_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_wishlist(
    wishlist_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ShoppingService(db)
    await service.remove_from_wishlist(current_user.id, wishlist_id)


# Search History
@router.get("/history", response_model=List[SearchHistoryResponse])
async def get_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ShoppingService(db)
    return await service.get_history(current_user.id)


@router.delete("/history", status_code=status.HTTP_204_NO_CONTENT)
async def clear_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ShoppingService(db)
    await service.clear_history(current_user.id)


# Dashboard
@router.get("/dashboard")
async def dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ShoppingService(db)
    history = await service.get_history(current_user.id)
    wishlist = await service.get_wishlist(current_user.id)
    return {
        "user": current_user.username,
        "total_searches": len(history),
        "wishlist_count": len(wishlist),
        "recent_searches": [h.query for h in history[:5]],
        "preferences": current_user.preferences,
    }
