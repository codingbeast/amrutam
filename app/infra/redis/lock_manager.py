# app/infra/redis/lock_manager.py
import asyncio
import uuid
from typing import Optional
from contextlib import asynccontextmanager

from redis.asyncio import Redis

LOCK_PREFIX = "lock:"
DEFAULT_LOCK_TTL = 15  # seconds


class RedisLockManager:
    """
    Simple Redis-based distributed lock manager.
    Uses SET NX EX for mutual exclusion.
    """

    def __init__(self, redis: Redis):
        self.redis = redis

    async def acquire_lock(
        self,
        key: str,
        ttl: int = DEFAULT_LOCK_TTL,
        retry_interval: float = 0.05,
        max_retries: int = 40,
    ) -> Optional[str]:
        """
        Try to acquire a lock on `key`.
        Returns lock token (value) if acquired, None otherwise.
        """
        lock_key = f"{LOCK_PREFIX}{key}"
        token = str(uuid.uuid4())

        for _ in range(max_retries):
            # SET key value NX EX ttl
            is_set = await self.redis.set(lock_key, token, nx=True, ex=ttl)
            if is_set:
                return token
            await asyncio.sleep(retry_interval)

        return None

    async def release_lock(self, key: str, token: str) -> bool:
        """
        Release a lock if token matches (avoid releasing someone else's lock).
        Uses a Lua script for atomic check-and-del.
        """
        lock_key = f"{LOCK_PREFIX}{key}"

        lua = """
        if redis.call("GET", KEYS[1]) == ARGV[1] then
          return redis.call("DEL", KEYS[1])
        else
          return 0
        end
        """

        result = await self.redis.eval(lua, 1, lock_key, token)
        return result == 1

    @asynccontextmanager
    async def lock(self, key: str, ttl: int = DEFAULT_LOCK_TTL):
        """
        Context-manager style usage:

        async with lock_manager.lock(f"slot:{slot_id}"):
            # safely mutate availability slot
        """
        token = await self.acquire_lock(key, ttl=ttl)
        if not token:
            raise TimeoutError(f"Failed to acquire lock for: {key}")

        try:
            yield
        finally:
            await self.release_lock(key, token)
