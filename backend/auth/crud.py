from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
from backend.db.models import User, FailedLogin, PasswordReset
from backend.auth.security import get_password_hash, verify_password, generate_reset_token
from backend.config import settings


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, email: str, password: str, full_name: Optional[str] = None) -> User:
    """Create a new user"""
    hashed_password = get_password_hash(password)
    db_user = User(
        email=email,
        hashed_password=hashed_password,
        full_name=full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, email: str, password: str, ip_address: Optional[str] = None) -> Optional[User]:
    """Authenticate user and handle failed login tracking"""
    user = get_user_by_email(db, email)
    
    if not user:
        return None
    
    # Check if account is locked
    if user.is_locked and user.locked_until:
        if datetime.utcnow() < user.locked_until:
            return None
        else:
            # Unlock account if lockout period has expired
            user.is_locked = False
            user.locked_until = None
            db.commit()
    
    # Verify password
    if not verify_password(password, user.hashed_password):
        # Record failed login
        failed_login = FailedLogin(user_id=user.id, ip_address=ip_address)
        db.add(failed_login)
        
        # Check failed login count in the last lockout duration
        cutoff_time = datetime.utcnow() - timedelta(minutes=settings.lockout_duration_minutes)
        recent_failures = db.query(FailedLogin).filter(
            FailedLogin.user_id == user.id,
            FailedLogin.attempted_at >= cutoff_time
        ).count()
        
        # Lock account if too many failures
        if recent_failures >= settings.max_failed_login_attempts:
            user.is_locked = True
            user.locked_until = datetime.utcnow() + timedelta(minutes=settings.lockout_duration_minutes)
        
        db.commit()
        return None
    
    # Clear failed logins on successful authentication
    db.query(FailedLogin).filter(FailedLogin.user_id == user.id).delete()
    db.commit()
    
    return user


def create_password_reset_token(db: Session, email: str) -> Optional[str]:
    """Create a password reset token"""
    user = get_user_by_email(db, email)
    if not user:
        return None
    
    # Invalidate existing tokens
    db.query(PasswordReset).filter(
        PasswordReset.user_id == user.id,
        PasswordReset.is_used == False
    ).update({"is_used": True})
    
    # Create new token
    token = generate_reset_token()
    reset = PasswordReset(
        user_id=user.id,
        token=token,
        expires_at=datetime.utcnow() + timedelta(hours=1)
    )
    db.add(reset)
    db.commit()
    
    return token


def reset_password_with_token(db: Session, token: str, new_password: str) -> bool:
    """Reset password using a valid token"""
    reset = db.query(PasswordReset).filter(
        PasswordReset.token == token,
        PasswordReset.is_used == False
    ).first()
    
    if not reset:
        return False
    
    # Check if token is expired
    if datetime.utcnow() > reset.expires_at:
        return False
    
    # Update password
    user = get_user_by_id(db, reset.user_id)
    if not user:
        return False
    
    user.hashed_password = get_password_hash(new_password)
    reset.is_used = True
    
    db.commit()
    return True
