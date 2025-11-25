from fastapi import APIRouter
from app.infra.db.session import AsyncSessionFactory
from app.infra.redis.client import redis_client

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/healthz")
async def healthz():
    """
    Liveness probe.
    Just check that the app process is alive.
    Avoid heavy checks here.
    """
    return {"status": "ok"}


@router.get("/readyz")
async def readyz():
    """
    Readiness probe.
    Check dependencies like DB and Redis.
    K8s will only send traffic to pod when this is 200.
    """
    # Check DB
    try:
        async with AsyncSessionFactory() as session:
            # simple ping
            await session.execute("SELECT 1")
    except Exception as e:
        return {"status": "error", "component": "database", "detail": str(e)}

    # Check Redis
    try:
        pong = await redis_client.ping()
        if not pong:
            return {"status": "error", "component": "redis", "detail": "no pong"}
    except Exception as e:
        return {"status": "error", "component": "redis", "detail": str(e)}

    return {"status": "ok"}
