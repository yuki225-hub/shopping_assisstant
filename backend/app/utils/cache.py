import json
from typing import Optional
from loguru import logger

try:
    import aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from app.config.settings import settings

_redis = None


async def get_redis():
    global _redis
    if not REDIS_AVAILABLE:
        return None
    if _redis is None:
        try:
            _redis = await aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")
            return None
    return _redis


async def cache_get(key: str) -> Optional[dict]:
    redis = await get_redis()
    if not redis:
        return None
    try:
        data = await redis.get(key)
        return json.loads(data) if data else None
    except Exception:
        return None


async def cache_set(key: str, value: dict, ttl: int = None) -> None:
    redis = await get_redis()
    if not redis:
        return
    try:
        await redis.setex(key, ttl or settings.CACHE_TTL, json.dumps(value))
    except Exception as e:
        logger.warning(f"Cache set failed: {e}")


async def cache_delete(key: str) -> None:
    redis = await get_redis()
    if not redis:
        return
    try:
        await redis.delete(key)
    except Exception:
        pass
