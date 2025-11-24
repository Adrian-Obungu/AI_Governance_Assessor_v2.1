from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import timedelta
from backend.db.database import get_db
from backend.auth.schemas import UserCreate, UserLogin, UserResponse, Token, PasswordResetRequest, PasswordResetConfirm
from backend.auth.crud import create_user, authenticate_user, get_user_by_email, create_password_reset_token, reset_password_with_token
from backend.auth.security import create_access_token
from backend.config import settings

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    existing_user = get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    db_user = create_user(db, user.email, user.password, user.full_name)
    return db_user


@router.post("/login", response_model=Token)
async def login(user_login: UserLogin, request: Request, db: Session = Depends(get_db)):
    """Authenticate user and return JWT token"""
    # Get client IP
    ip_address = request.client.host if request.client else None
    
    # Authenticate
    user = authenticate_user(db, user_login.email, user_login.password, ip_address)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password, or account is locked",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def request_password_reset(reset_request: PasswordResetRequest, db: Session = Depends(get_db)):
    """Request a password reset token"""
    token = create_password_reset_token(db, reset_request.email)
    
    # Always return success to prevent email enumeration
    # In production, send email with token here
    if settings.email_enabled and token:
        # Mock email sending - in production, integrate with email service
        print(f"Password reset token for {reset_request.email}: {token}")
    
    return {"message": "If the email exists, a password reset link has been sent"}


@router.post("/reset-password/confirm", status_code=status.HTTP_200_OK)
async def confirm_password_reset(reset_confirm: PasswordResetConfirm, db: Session = Depends(get_db)):
    """Reset password using a valid token"""
    success = reset_password_with_token(db, reset_confirm.token, reset_confirm.new_password)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )
    
    return {"message": "Password successfully reset"}
