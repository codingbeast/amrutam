from __future__ import annotations

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security.passwords import hash_password, verify_password
from app.core.security.jwt import create_access_token, create_refresh_token
from app.domain.identity.dto import RegisterUserRequest, LoginRequest, TokenResponse
from app.domain.identity.models import User
from app.domain.identity.repository import UserRepository


class IdentityService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = UserRepository(session)

    async def register_user(self, data: RegisterUserRequest) -> User:
        existing = await self.repo.get_by_email(data.email)
        if existing:
            raise ValueError("Email already registered")

        user = await self.repo.create_user(
            email=data.email,
            hashed_password=hash_password(data.password),
            role=data.role,
        )
        return user

    async def authenticate(self, data: LoginRequest) -> Optional[User]:
        user = await self.repo.get_by_email(data.email)
        if not user:
            return None
        if not verify_password(data.password, user.hashed_password):
            return None
        if not user.is_active:
            return None
        return user

    async def create_tokens_for_user(self, user: User) -> TokenResponse:
        access = create_access_token(subject=str(user.id), extra={"role": user.role})
        refresh = create_refresh_token(subject=str(user.id))
        return TokenResponse(access_token=access, refresh_token=refresh)
