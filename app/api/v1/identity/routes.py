from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.infra.db.session import get_session
from app.domain.identity.dto import (
    RegisterUserRequest,
    LoginRequest,
    TokenResponse,
    UserResponse,
)
from app.domain.identity.service import IdentityService
from app.core.security.deps import get_current_user
from app.domain.identity.models import User

router = APIRouter(prefix="/v1/identity", tags=["identity"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    payload: RegisterUserRequest,
    session: AsyncSession = Depends(get_session),
):
    service = IdentityService(session)

    try:
        user = await service.register_user(payload)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return user


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    session: AsyncSession = Depends(get_session),
):
    service = IdentityService(session)
    user = await service.authenticate(payload)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    tokens = await service.create_tokens_for_user(user)
    return tokens


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user


@router.get("/health")
async def health_check():
    return {"status": "identity router OK"}
