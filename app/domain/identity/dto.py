from uuid import UUID
from pydantic import BaseModel, EmailStr, Field
from app.domain.identity.models import UserRole


class AdminCreateUserRequest(BaseModel):
    email: EmailStr
    password: str
    role: UserRole  # admin can create ANY role

class RegisterUserRequest(BaseModel):
    email: EmailStr
    password: str
    role: UserRole = Field(..., pattern="^(patient|doctor)$")
    #block admin registration


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    
class LoginRequestOauth(BaseModel):
    username : EmailStr
    password : str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    role: str
    is_active: bool

    model_config = {"from_attributes": True}

class RefreshTokenRequest(BaseModel):
    refresh_token: str