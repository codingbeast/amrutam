from sqlalchemy import select

from app.infra.db.session import async_session_factory
from app.domain.identity.models import User, UserRole
from app.core.security.passwords import hash_password
from app.core.config.settings import settings


async def create_initial_admin():
    """
    Create an admin only if none exists.
    """

    async with async_session_factory() as session:
        # check existing admin
        result = await session.execute(
            select(User).where(User.role == UserRole.admin)
        )
        admin_exists = result.scalar_one_or_none()

        if admin_exists:
            return  # Admin already exists, do nothing

        # create default admin
        admin = User(
            email=settings.DEFAULT_ADMIN_EMAIL,
            hashed_password=hash_password(settings.DEFAULT_ADMIN_PASSWORD),
            role=UserRole.admin,
            is_active=True,
        )

        session.add(admin)
        await session.commit()

        print("✔ Initial admin created")
