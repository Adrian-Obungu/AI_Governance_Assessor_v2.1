from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema"""

    email: EmailStr
    full_name: str | None = None


class UserCreate(UserBase):
    """Schema for user creation"""

    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    """Schema for user login"""

    email: EmailStr
    password: str


class UserResponse(UserBase):
    """Schema for user response"""

    id: int
    is_active: bool
    is_locked: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """JWT token response"""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data"""

    email: str | None = None


class PasswordResetRequest(BaseModel):
    """Request password reset"""

    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Confirm password reset with token"""

    token: str
    new_password: str = Field(..., min_length=8)
