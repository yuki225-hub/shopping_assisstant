import time
import uuid
from fastapi import Request
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())[:8]
        start = time.time()

        logger.info(f"[{request_id}] {request.method} {request.url.path}")

        try:
            response = await call_next(request)
            duration = round((time.time() - start) * 1000, 2)
            logger.info(f"[{request_id}] {response.status_code} - {duration}ms")
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = f"{duration}ms"
            return response
        except Exception as e:
            logger.error(f"[{request_id}] Unhandled error: {e}")
            raise
