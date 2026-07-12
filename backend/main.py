from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger
import os

from app.config.settings import settings
from app.database.session import init_db
from app.middleware.logging import LoggingMiddleware
from app.api.auth.routes import router as auth_router
from app.api.shopping.routes import router as shopping_router
from app.core.exceptions import AppException
from app.core.logging import setup_logging

# Setup logging
os.makedirs("logs", exist_ok=True)
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    await init_db()
    logger.info("Database initialized")
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
## Multi-Agent Shopping Assistant API

An AI-powered shopping platform that searches, compares, and recommends products
across multiple e-commerce platforms using specialized AI agents.

### Agents
- **Product Search Agent** - Searches across Amazon, Flipkart, Meesho, Myntra, Ajio, Croma, Reliance Digital
- **Price Comparison Agent** - Compares prices and finds best value
- **Review Analysis Agent** - NLP-based sentiment analysis of reviews
- **Recommendation Agent** - Multi-factor scoring for personalized recommendations

### Authentication
Use JWT Bearer token. Register → Login → Use access_token in Authorization header.
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom logging middleware
app.add_middleware(LoggingMiddleware)

# Rate limiting
try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded

    limiter = Limiter(key_func=get_remote_address, default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"])
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    logger.info("Rate limiting enabled")
except ImportError:
    logger.warning("slowapi not available, rate limiting disabled")


# Global exception handler
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


# Routers - API v1
app.include_router(auth_router, prefix="/api/v1")
app.include_router(shopping_router, prefix="/api/v1")


@app.get("/", tags=["Health"])
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy", "environment": settings.ENVIRONMENT}
