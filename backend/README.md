# Multi-Agent Shopping Assistant - Backend

An AI-powered shopping platform that searches, compares, and recommends products across multiple e-commerce platforms using specialized AI agents.

## Architecture

```
User Request
    ↓
CoordinatorAgent
    ├── ProductSearchAgent  → Amazon, Flipkart, Meesho, Myntra, Ajio, Croma, Reliance Digital
    ├── PriceComparisonAgent → Lowest/Highest/Average price, Best value
    ├── ReviewAnalysisAgent  → NLP Sentiment Analysis (HuggingFace / Keyword fallback)
    └── RecommendationAgent  → Multi-factor scoring (0-100)
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI + Uvicorn |
| Database | SQLite (dev) / PostgreSQL (prod) |
| ORM | SQLAlchemy 2.0 (async) |
| Auth | JWT (python-jose) + bcrypt |
| NLP | HuggingFace Transformers (optional) |
| Cache | Redis (optional) |
| Validation | Pydantic v2 |
| Testing | pytest + pytest-asyncio |
| Container | Docker + Docker Compose |

## Quick Start

### 1. Setup Environment

```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# Edit .env with your settings
```

### 2. Run Development Server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Access API

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health: http://localhost:8000/health

## Docker

```bash
# Development
docker-compose up --build

# Production
SECRET_KEY=your-secret-key docker-compose up -d
```

## API Endpoints

### Authentication (`/api/v1/auth`)
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/register` | No | Register new user |
| POST | `/login` | No | Login, get JWT tokens |
| POST | `/refresh` | No | Refresh access token |
| POST | `/logout` | Yes | Logout |
| POST | `/forgot-password` | No | Request password reset |
| POST | `/reset-password` | No | Reset password with token |
| GET | `/profile` | Yes | Get user profile |
| PUT | `/profile` | Yes | Update user profile |

### Shopping (`/api/v1`)
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/search?q=laptop` | Optional | Search products across all platforms |
| GET | `/product/{id}` | No | Get product by ID |
| POST | `/compare` | No | Compare specific products |
| POST | `/recommend` | No | Get recommendations for products |
| POST | `/analyze-reviews` | No | Analyze custom reviews |
| GET | `/wishlist` | Yes | Get user wishlist |
| POST | `/wishlist` | Yes | Add to wishlist |
| DELETE | `/wishlist/{id}` | Yes | Remove from wishlist |
| GET | `/history` | Yes | Get search history |
| DELETE | `/history` | Yes | Clear search history |
| GET | `/dashboard` | Yes | User dashboard |

## Search Query Parameters

```
GET /api/v1/search?q=laptop&platforms=amazon,flipkart&min_price=20000&max_price=80000&min_rating=4&sort_by=price_asc&page=1&page_size=20
```

## Sample Response

```json
{
  "query": "laptop",
  "total_results": 30,
  "products": [...],
  "price_comparison": {
    "lowest_price": 35000,
    "highest_price": 85000,
    "average_price": 52000,
    "best_value_product": "...",
    "cheapest_product": "...",
    "comparison_table": [...]
  },
  "review_analysis": {
    "overall_sentiment": "positive",
    "positive_percent": 72.5,
    "negative_percent": 15.0,
    "neutral_percent": 12.5,
    "common_pros": ["excellent", "quality", "fast"],
    "common_cons": ["expensive"],
    "summary": "...",
    "recommendation_confidence": 0.73
  },
  "recommendation": {
    "best_overall": "Product Title",
    "best_budget": "Budget Product",
    "best_premium": "Premium Product",
    "score": 87.5,
    "reason": "...",
    "pros": [...],
    "cons": [...],
    "explanation": "..."
  }
}
```

## Running Tests

```bash
pytest
pytest tests/test_agents.py -v
pytest tests/test_auth.py -v
pytest --cov=app --cov-report=html
```

## Adding a New Platform

1. Create adapter in `app/agents/product_search/adapters.py`:

```python
class NewPlatformAdapter(BaseAdapter):
    platform_name = "NewPlatform"

    async def search(self, query: str, **kwargs) -> List[ProductSchema]:
        # Implement scraping or API call
        return [self._normalize(product_data)]
```

2. Register in `app/agents/product_search/agent.py`:

```python
ALL_ADAPTERS = {
    ...
    "newplatform": NewPlatformAdapter(),
}
```

## Production Checklist

- [ ] Change `SECRET_KEY` in `.env`
- [ ] Set `ENVIRONMENT=production`
- [ ] Use PostgreSQL (`DATABASE_URL=postgresql+asyncpg://...`)
- [ ] Configure Redis for caching
- [ ] Set up SMTP for password reset emails
- [ ] Configure `ALLOWED_ORIGINS` for your frontend domain
- [ ] Enable HTTPS (use nginx reverse proxy)
- [ ] Set up log rotation
- [ ] Configure monitoring (e.g., Prometheus + Grafana)
