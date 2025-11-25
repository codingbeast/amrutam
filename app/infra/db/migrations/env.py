import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection

from alembic import context
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.core.config.settings import settings
from app.infra.db.base import Base

# --- IMPORT ALL MODELS (Auto-Discovery) ---
# IMPORTANT: import every model folder so Alembic can detect them
from app.modules.identity.infrastructure.models import *
from app.modules.doctors.infrastructure.models import *
from app.modules.availability.infrastructure.models import *
from app.modules.booking.infrastructure.models import *
from app.modules.consultations.infrastructure.models import *
from app.modules.prescriptions.infrastructure.models import *
from app.modules.payments.infrastructure.models import *
from app.modules.audit.infrastructure.models import *
from app.modules.notifications.infrastructure.models import *

# -------------------------------------------------------
# ALEMBIC CONFIG
# -------------------------------------------------------
config = context.config

# If using a .ini file for logging:
if config.config_file_name:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


# -------------------------------------------------------
# DATABASE URL (ASYNC)
# -------------------------------------------------------
def get_url() -> str:
    return (
        f"postgresql+asyncpg://{settings.DB_USER}:"
        f"{settings.DB_PASSWORD}@{settings.DB_HOST}:"
        f"{settings.DB_PORT}/{settings.DB_NAME}"
    )


# -------------------------------------------------------
# RUN MIGRATIONS (ONLINE MODE - ASYNC)
# -------------------------------------------------------
async def run_migrations_online():
    url = get_url()

    connectable: AsyncEngine = create_async_engine(
        url,
        future=True,
        echo=False,
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


# -------------------------------------------------------
# RUN MIGRATIONS (OFFLINE MODE)
# -------------------------------------------------------
def run_migrations_offline():
    url = get_url()

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


# -------------------------------------------------------
# GENERIC RUNNER FOR BOTH
# -------------------------------------------------------
def do_run_migrations(connection: Connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,     # detect column type changes
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


# -------------------------------------------------------
# MAIN ENTRY
# -------------------------------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
