from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    Index,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from backend.db.database import Base


class User(Base):
    """User model for authentication and authorization"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_locked = Column(Boolean, default=False)
    locked_until = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    assessments = relationship("Assessment", back_populates="user")
    failed_logins = relationship("FailedLogin", back_populates="user")
    password_resets = relationship("PasswordReset", back_populates="user")


class FailedLogin(Base):
    """Track failed login attempts for account lockout"""

    __tablename__ = "failed_logins"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    attempted_at = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String(45), nullable=True)

    # Relationships
    user = relationship("User", back_populates="failed_logins")


class PasswordReset(Base):
    """Single-use password reset tokens"""

    __tablename__ = "password_resets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String(255), unique=True, index=True, nullable=False)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)

    # Relationships
    user = relationship("User", back_populates="password_resets")


class Assessment(Base):
    """AI Governance Assessment"""

    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    schema_version = Column(String(32), default="1.0", nullable=False)
    status = Column(String(20), default="draft", nullable=False)  # draft, in_progress, completed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="assessments")
    results = relationship(
        "AssessmentResult", back_populates="assessment", cascade="all, delete-orphan"
    )
    __table_args__ = (
        CheckConstraint(
            "status IN ('draft', 'in_progress', 'completed')",
            name="ck_assessments_status",
        ),
        CheckConstraint(
            "status <> 'completed' OR completed_at IS NOT NULL",
            name="ck_assessments_completed_at",
        ),
        Index("ix_assessments_user_created_at", "user_id", "created_at"),
        Index("ix_assessments_user_status", "user_id", "status"),
    )


class AssessmentResult(Base):
    """Versioned assessment results with scores"""

    __tablename__ = "assessment_results"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    category = Column(
        String(100), nullable=False
    )  # data_privacy, model_risk, ethics, compliance
    questions = Column(JSON, nullable=False)  # Store questions and answers
    questionnaire_version = Column(String(32), nullable=False, default="1.0")
    questionnaire_snapshot = Column(JSON, nullable=False, default=dict)
    scoring_version = Column(String(32), nullable=False, default="1.0")
    score = Column(Integer, nullable=False)  # 0-100
    maturity_level = Column(
        String(50), nullable=False
    )  # initial, developing, defined, managed, optimized
    recommendations = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    assessment = relationship("Assessment", back_populates="results")
    __table_args__ = (
        UniqueConstraint(
            "assessment_id",
            "category",
            name="uq_assessment_results_assessment_category",
        ),
        Index("ix_assessment_results_assessment_category", "assessment_id", "category"),
        CheckConstraint(
            "category IN ('data_privacy', 'model_risk', 'ethics', 'compliance')",
            name="ck_assessment_results_category",
        ),
    )
