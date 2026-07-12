from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class ProductSchema(BaseModel):
    id: Optional[int] = None
    platform: str
    external_id: Optional[str] = None
    title: str
    category: Optional[str] = None
    price: Optional[float] = None
    original_price: Optional[float] = None
    discount: Optional[float] = None
    offer: Optional[str] = None
    availability: bool = True
    seller: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    image_url: Optional[str] = None
    product_url: Optional[str] = None
    relevance_score: Optional[float] = None
    specifications: Dict[str, Any] = {}
    delivery_time: Optional[str] = None

    model_config = {"from_attributes": True}


class PriceComparisonSchema(BaseModel):
    lowest_price: Optional[float]
    highest_price: Optional[float]
    average_price: Optional[float]
    best_value_product: Optional[str]
    cheapest_product: Optional[str]
    premium_product: Optional[str]
    comparison_table: List[Dict[str, Any]]


class ReviewAnalysisSchema(BaseModel):
    overall_sentiment: str
    positive_percent: float
    negative_percent: float
    neutral_percent: float
    common_pros: List[str]
    common_cons: List[str]
    summary: str
    recommendation_confidence: float
    fake_review_flag: bool = False


class RecommendationSchema(BaseModel):
    best_overall: Optional[str]
    best_budget: Optional[str]
    best_premium: Optional[str]
    best_overall_price: Optional[float] = None
    best_budget_price: Optional[float] = None
    best_premium_price: Optional[float] = None
    best_overall_rating: Optional[float] = None
    best_budget_rating: Optional[float] = None
    best_premium_rating: Optional[float] = None
    best_overall_platform: Optional[str] = None
    best_budget_platform: Optional[str] = None
    best_premium_platform: Optional[str] = None
    best_overall_url: Optional[str] = None
    best_budget_url: Optional[str] = None
    best_premium_url: Optional[str] = None
    # Real backend values for the recommendation card
    best_overall_reviews: Optional[int] = None
    best_overall_delivery: Optional[str] = None
    best_overall_sentiment: Optional[float] = None
    category: Optional[str] = None
    score: float
    reason: str
    pros: List[str]
    cons: List[str]
    explanation: str


class SearchResponse(BaseModel):
    query: str
    total_results: int
    products: List[ProductSchema]
    price_comparison: PriceComparisonSchema
    review_analysis: ReviewAnalysisSchema
    recommendation: RecommendationSchema
    cached: bool = False


class SearchRequest(BaseModel):
    query: str
    platforms: Optional[List[str]] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_rating: Optional[float] = None
    sort_by: Optional[str] = "relevance"
    page: int = 1
    page_size: int = 20


class WishlistCreate(BaseModel):
    product_id: int
    note: Optional[str] = None


class WishlistResponse(BaseModel):
    id: int
    product: ProductSchema
    note: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class SearchHistoryResponse(BaseModel):
    id: int
    query: str
    result_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class CompareRequest(BaseModel):
    product_ids: List[int]


class AnalyzeReviewsRequest(BaseModel):
    reviews: List[str]
    product_title: Optional[str] = None
