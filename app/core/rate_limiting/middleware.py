# app/core/rate_limiting/middleware.py
import time
from typing import Callable

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from redis.asyncio import Redis

RATE_LIMIT_PREFIX = "rl:"
DEFAULT_WINDOW = 60       # seconds
DEFAULT_MAX_REQUESTS = 100


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Very simple fixed-window rate limiter.
    Keyed by user_id (if auth) or client IP.
    """

    def __init__(
        self,
        app,
        redis: Redis,
        max_requests: int = DEFAULT_MAX_REQUESTS,
        window_seconds: int = DEFAULT_WINDOW,
    ):
        super().__init__(app)
        self.redis = redis
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    async def dispatch(self, request: Request, call_next: Callable):
        # 1. Identify client
        client_ip = request.client.host if request.client else "unknown"
        # Optionally use user_id from auth instead:
        # user_id = getattr(request.state, "user_id", None) or client_ip
        key = client_ip

        # 2. Compute window key
        current_window = int(time.time()) // self.window_seconds
        redis_key = f"{RATE_LIMIT_PREFIX}{key}:{current_window}"

        # 3. Increment counter
        count = await self.redis.incr(redis_key)

        if count == 1:
            await self.redis.expire(redis_key, self.window_seconds)

        # 4. Enforce limit
        if count > self.max_requests:
            raise HTTPException(
                status_code=429,
                detail="Too Many Requests",
            )

        # 5. Let request proceed
        response = await call_next(request)

        # Optionally expose headers
        remaining = max(self.max_requests - count, 0)
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)

        return response
