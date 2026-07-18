from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List
import os


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Multi-Agent Shopping Assistant"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./shopping.db"

    # JWT
    SECRET_KEY: str = "change-this-secret-key-in-production-32chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL: int = 300

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "noreply@shoppingassistant.com"

    # HuggingFace
    HF_MODEL_NAME: str = "cardiffnlp/twitter-roberta-base-sentiment-latest"

    # RapidAPI (real product data)
    RAPIDAPI_KEY: str = ""

    # Google OAuth Keys for Sign-In 🌟
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""

    # Google Custom Search API (product images + exact product URLs)
    GOOGLE_API_KEY: str = ""
    GOOGLE_CSE_ID: str = ""

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    @property
    def allowed_origins_list(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # 🟢 Extra key constraints errors crash bypass settings!


settings = Settings()