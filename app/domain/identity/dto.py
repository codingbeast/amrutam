from pydantic import BaseModel, EmailStr, Field


class RegisterUserRequest(BaseModel):
     # patient | doctor | admin
    email: EmailStr
    password: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "user@example.com",
                "password": "stringst"
            }
        }
    }


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    role: str
    is_active: bool

    model_config = {"from_attributes": True}
