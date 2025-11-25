# app/infra/redis/client.py
from redis.asyncio import Redis
from app.core.config.settings import settings

redis_client = Redis(
    host=settings.REDIS_HOST,
    port=int(settings.REDIS_PORT),
    decode_responses=False,
)
