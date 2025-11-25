from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from jose import JWTError, jwt

from app.core.config.settings import settings
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN
from app.domain.identity.repository import UserRepository
from app.infra.db.session import get_session
from app.domain.identity.models import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/identity/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session=Depends(get_session),
) -> User:
    """
    Extract user from JWT token, verify & fetch from DB.
    """

    try:
        payload = decode_token(token)
    except ValueError:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    repo = UserRepository(session)
    user = await repo.get_by_id(user_id)

    if not user:
        raise HTTPException(404, "User not found")

    if not user.is_active:
        raise HTTPException(HTTP_403_FORBIDDEN, "Inactive user")

    return user


async def get_current_admin(user: User = Depends(get_current_user)) -> User:
    """
    Restrict access to admin users only.
    """
    if user.role != UserRole.admin:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user


def _create_token(data: Dict[str, Any], expires_delta: timedelta) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def create_access_token(subject: str, extra: Optional[Dict[str, Any]] = None) -> str:
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    data: Dict[str, Any] = {"sub": subject}
    if extra:
        data.update(extra)
    return _create_token(data, expires_delta)


def create_refresh_token(subject: str) -> str:
    expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    data: Dict[str, Any] = {"sub": subject, "type": "refresh"}
    return _create_token(data, expires_delta)


def decode_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError as exc:
        raise ValueError("Invalid token") from exc
