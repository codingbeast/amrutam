from fastapi import APIRouter
from sqlalchemy import text
from app.infra.db.session import async_session_factory
from app.infra.redis.client import redis_client
router = APIRouter(prefix="/system", tags=["system"])


@router.get("/healthz")
async def healthz():
    """
    Liveness probe.
    Just checks that the app process is alive.
    """
    return {"status": "ok"}


@router.get("/readyz")
async def readyz():
    """
    Readiness probe.
    Checks DB and Redis.
    K8s sends traffic only if this returns 200.
    """

    # ---- DB Check ----
    try:
        async with async_session_factory() as session:   # ✅ FIXED
            await session.execute(text("SELECT 1"))
    except Exception as e:
        return {
            "status": "error",
            "component": "database",
            "detail": str(e),
        }

    # ---- Redis Check ----
    try:
        pong = await redis_client.ping()
        if not pong:
            return {
                "status": "error",
                "component": "redis",
                "detail": "No PONG",
            }
    except Exception as e:
        return {
            "status": "error",
            "component": "redis",
            "detail": str(e),
        }

    return {"status": "ok"}
