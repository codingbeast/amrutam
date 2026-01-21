from __future__ import annotations
from uuid import UUID
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.identity.models import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: str | UUID) -> Optional[User]:
        stmt = select(User).where(User.id == user_id)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def create_user(self, *, email: str, hashed_password: str, role: str) -> User:
        user = User(email=email, hashed_password=hashed_password, role=role)
        self.session.add(user)
        await self.session.flush()  # get id
        return user
