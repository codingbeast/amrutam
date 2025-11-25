from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.infra.db.session import get_session
from app.core.security.deps import get_current_user
from app.domain.identity.dto import AdminCreateUserRequest, UserResponse
from app.domain.identity.models import UserRole
from app.domain.identity.service import IdentityService

router = APIRouter(prefix="/admin", tags=["admin"])

@router.post("/users/create", response_model=UserResponse)
async def admin_create_user(
    payload: AdminCreateUserRequest,
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_user),
):
    # Only admin can create users
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Only admin can create users")

    # Pass session to service
    service = IdentityService(session)

    user = await service.create_user_from_admin(payload)
    return user

# Admin health check
@router.get("/health")
async def health_check():
    return {"status": "admin router OK"}

