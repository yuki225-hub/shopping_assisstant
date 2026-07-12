import pytest
from app.agents.product_search.agent import ProductSearchAgent
from app.agents.price_compare.agent import PriceComparisonAgent
from app.agents.review_analysis.agent import ReviewAnalysisAgent
from app.agents.recommendation.agent import RecommendationAgent
from app.schemas.product import ProductSchema, PriceComparisonSchema, ReviewAnalysisSchema

pytestmark = pytest.mark.asyncio

MOCK_PRODUCTS = [
    ProductSchema(platform="Amazon", title="Test Laptop A", price=45000, original_price=55000,
                  discount=18.2, rating=4.5, review_count=1200, availability=True, delivery_time="1-2 days"),
    ProductSchema(platform="Flipkart", title="Test Laptop B", price=42000, original_price=50000,
                  discount=16.0, rating=4.2, review_count=800, availability=True, delivery_time="2-3 days"),
    ProductSchema(platform="Croma", title="Test Laptop C", price=48000, original_price=52000,
                  discount=7.7, rating=3.8, review_count=300, availability=False, delivery_time="3-5 days"),
]


async def test_product_search_agent():
    agent = ProductSearchAgent()
    products = await agent.search("laptop")
    assert len(products) > 0
    assert all(p.platform for p in products)
    assert all(p.title for p in products)


async def test_product_search_platform_filter():
    agent = ProductSearchAgent()
    products = await agent.search("phone", platforms=["amazon"])
    assert all(p.platform == "Amazon" for p in products)


async def test_price_comparison_agent():
    agent = PriceComparisonAgent()
    result = agent.compare(MOCK_PRODUCTS)
    assert result.lowest_price == 42000
    assert result.highest_price == 48000
    assert result.average_price == pytest.approx(45000, rel=0.01)
    assert result.cheapest_product == "Test Laptop B"
    assert len(result.comparison_table) == 3


async def test_price_comparison_empty():
    agent = PriceComparisonAgent()
    result = agent.compare([])
    assert result.lowest_price is None
    assert result.comparison_table == []


async def test_review_analysis_agent():
    agent = ReviewAnalysisAgent()
    result = agent.analyze(MOCK_PRODUCTS)
    assert result.overall_sentiment in ["positive", "negative", "mixed", "neutral"]
    assert 0 <= result.positive_percent <= 100
    assert 0 <= result.negative_percent <= 100
    assert result.recommendation_confidence >= 0


async def test_recommendation_agent():
    price_comp = PriceComparisonAgent().compare(MOCK_PRODUCTS)
    review = ReviewAnalysisAgent().analyze(MOCK_PRODUCTS)
    agent = RecommendationAgent()
    result = agent.recommend(MOCK_PRODUCTS, price_comp, review)
    assert result.best_overall is not None
    assert 0 <= result.score <= 100
    assert result.reason
    assert result.explanation


async def test_recommendation_empty():
    agent = RecommendationAgent()
    price_comp = PriceComparisonAgent().compare([])
    review = ReviewAnalysisAgent().analyze([])
    result = agent.recommend([], price_comp, review)
    assert result.score == 0
