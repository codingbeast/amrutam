"""main entry point"""

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from contextlib import asynccontextmanager
# Routers
from app.api.v1.identity.routes import router as identity_router
from app.api.v1.doctors.routes import router as doctors_router
from app.api.v1.availability.routes import router as availability_router
from app.api.v1.booking.routes import router as booking_router
from app.api.v1.consultations.routes import router as consultations_router
from app.api.v1.prescriptions.routes import router as prescriptions_router
from app.api.v1.payments.routes import router as payments_router
from app.api.v1.search.routes import router as search_router
from app.api.v1.analytics.routes import router as analytics_router
from app.api.v1.admin.routes import router as admin_router
from app.api.v1.system.routes import router as system_router

# Middleware
from app.infra.db.startup import create_initial_admin
from app.infra.redis.client import redis_client
from app.core.idempotency.middleware import IdempotencyMiddleware
from app.core.rate_limiting.middleware import RateLimitMiddleware


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Startup
    await create_initial_admin()
    yield
    # Shutdown (optional cleanup here)
# -----------------------------------------------------------
# CREATE APP (NO LIFESPAN USED ANYMORE)
# -----------------------------------------------------------
app = FastAPI(title="Amrutam Backend", lifespan=lifespan)

# -----------------------------------------------------------
# ADD PROMETHEUS INSTRUMENTATION (BEFORE STARTUP)
# -----------------------------------------------------------
Instrumentator().instrument(app).expose(app, endpoint="/metrics")


# -----------------------------------------------------------
# ADD MIDDLEWARE
# -----------------------------------------------------------
app.add_middleware(IdempotencyMiddleware, redis=redis_client)
app.add_middleware(
    RateLimitMiddleware,
    redis=redis_client,
    max_requests=100,
    window_seconds=60,
)


# -----------------------------------------------------------
# INCLUDE ROUTERS
# -----------------------------------------------------------
app.include_router(identity_router)
app.include_router(doctors_router)
app.include_router(availability_router)
app.include_router(booking_router)
app.include_router(consultations_router)
app.include_router(prescriptions_router)
app.include_router(payments_router)
app.include_router(search_router)
app.include_router(analytics_router)
app.include_router(admin_router)
app.include_router(system_router)
