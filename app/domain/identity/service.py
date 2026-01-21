from __future__ import annotations

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.core.security.passwords import hash_password, verify_password
from app.core.security.jwt import create_access_token, create_refresh_token
from app.domain.identity.dto import AdminCreateUserRequest, RegisterUserRequest, LoginRequest, TokenResponse
from app.domain.identity.models import User, UserRole
from app.domain.identity.repository import UserRepository
from app.core.security.jwt import (
    create_access_token,
    create_refresh_token,
    decode_token,
)

class IdentityService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = UserRepository(session)
    # ---- internal helper used by both register flows ----
    async def _create_user(
        self,
        *,
        email: str,
        password: str,
        role: UserRole,
    ) -> User:
        existing = await self.repo.get_by_email(email)
        if existing:
            raise ValueError("User with this email already exists")

        user = User(
            email=email,
            hashed_password=hash_password(password),
            role=role,
            is_active=True,
        )
        self.session.add(user)
        await self.session.flush()  # so user.id is populated
        return user
    
    # ---------- PUBLIC /v1/identity/register ----------
    async def register_user(self, data: RegisterUserRequest) -> User:
        # Restrict public registration to patient/doctor only
        if data.role not in (UserRole.patient, UserRole.doctor):
            raise ValueError("Only patient/doctor can self-register")

        user = await self._create_user(
            email=data.email,
            password=data.password,
            role=data.role,
        )
        return user
    # ---------- ADMIN /v1/admin/users/create ----------
    async def create_user_from_admin(self, data: AdminCreateUserRequest) -> User:
        # Here we trust the caller is already checked as admin in the route
        user = await self._create_user(
            email=data.email,
            password=data.password,
            role=data.role,   # can be admin/doctor/patient
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
        access = create_access_token(
            subject=str(user.id),
            extra={"role": user.role},
        )
        refresh = create_refresh_token(subject=str(user.id))
        return TokenResponse(
            access_token=access,
            refresh_token=refresh,
            token_type="bearer",
        )

    async def refresh_tokens(self, refresh_token: str) -> TokenResponse:
        # 1. Decode & validate
        try:
            payload = decode_token(refresh_token)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )

        # 2. Load user
        user = await self.repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )

        # 3. Issue fresh access + refresh
        return await self.create_tokens_for_user(user)