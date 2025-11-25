# app/core/idempotency/middleware.py
import json
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from redis.asyncio import Redis

IDEMPOTENCY_PREFIX = "idmp:"
DEFAULT_TTL = 60 * 10  # 10 minutes


class IdempotencyMiddleware(BaseHTTPMiddleware):
    """
    Handles idempotent writes based on Idempotency-Key header.
    For POST/PUT/PATCH/DELETE only.
    Stores serialized response in Redis and replays on duplicate.
    """

    def __init__(self, app, redis: Redis):
        super().__init__(app)
        self.redis = redis

    async def dispatch(self, request: Request, call_next: Callable):
        method = request.method.upper()

        if method not in ("POST", "PUT", "PATCH", "DELETE"):
            return await call_next(request)

        key = request.headers.get("Idempotency-Key")
        if not key:
            # You can also choose to raise HTTPException(400, ...) here
            return await call_next(request)

        redis_key = f"{IDEMPOTENCY_PREFIX}{key}"

        # Check if we have a stored response
        cached = await self.redis.get(redis_key)
        if cached:
            data = json.loads(cached)
            return Response(
                content=data["body"],
                status_code=data["status_code"],
                headers=data["headers"],
                media_type=data.get("media_type") or "application/json",
            )

        # No cached response, execute the request
        response: Response = await call_next(request)

        # Only store successful or "definitive" responses (configurable)
        if response.status_code < 500:
            body = b""
            async for chunk in response.body_iterator:
                body += chunk

            # Replayable body iterator
            async def new_body_iter():
                yield body

            response.body_iterator = new_body_iter()

            cache_payload = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": body.decode("utf-8", errors="ignore"),
                "media_type": response.media_type,
            }
            await self.redis.setex(
                redis_key,
                DEFAULT_TTL,
                json.dumps(cache_payload),
            )

        return response
